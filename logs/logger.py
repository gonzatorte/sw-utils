from _socket import SOCK_DGRAM, gethostbyname, gaierror
from logging import Logger
import logging
import logging.handlers
import re
import sys
import inspect
from traceback import format_exception
from sw_utils.dummy_obj import DummyObj
from sw_utils.lang import param_get
import traceback
from sw_utils.logs.constants import TRACE_LVL
from sw_utils.logs.utils import pre_log


class SwLogger(Logger):
    aws = None
    instanceId = 'No'
    verb_log_formatter = []
    log_verb = 0
    get_custom_handler_function = None
    singleton_sentry_handler = None
    home_dir = None

    @classmethod
    def configure(cls, *args, **kwargs):
        if len(args) != 0 and len(kwargs.items()) != 0:
            raise Exception('No se puede usar invocacion por key y por posicion juntos...')
        cls.aws = param_get(args, kwargs, 0, 'aws')
        cls.instanceId = param_get(args, kwargs, 1, 'instanceId')
        cls.verb_log_formatter = param_get(args, kwargs, 2, 'verb_log_formatter')
        cls.log_verb = param_get(args, kwargs, 3, 'log_verb')
        cls.get_custom_handler_function = param_get(args, kwargs, 4, 'get_custom_handler_function', None)
        cls.appName = param_get(args, kwargs, 5, 'appName')
        cls.home_dir = param_get(args, kwargs, 6, 'home_dir', None)
        return (args[7:], kwargs)

    def __init__(self, name='', level=TRACE_LVL):
        self.file_handler = None
        self.sentry_handler = None
        self.console_handler = None
        self.syslog_handler = None
        self.socket_handler = None
        self.custom_handler = None
        self.verbosity = self.log_verb
        super(SwLogger, self).__init__(name=name, level=level)
        if self.aws:
            self.init_file_handler()
            self.init_sentry_handler()
            self.init_syslog_handler()
        else:
            self.init_console_handler()
        self.init_custom_handler()

    def _msg_format(self, msg, *args, **kwargs):
        try:
            if (type(msg) is str) or (type(msg) is unicode):
                return msg
            objs = [msg] + list(args)
            for i in xrange(len(objs)):
                if not isinstance(objs[i], BaseException):
                    objs[i] = str(objs[i])
                else:
                    tb = sys.exc_info()[2]
                    proc_objs = map(lambda ex: ','.join(format_exception(type(ex), ex, tb, 10)), objs)
                    objs = proc_objs
                    break
            return "\n".join(objs)
        except BaseException as e:
            return "SW LOGGER FORMATTING ERROR"

    def init_sentry_handler(self):
        if self.singleton_sentry_handler:
            self.sentry_handler = self.singleton_sentry_handler
            self.addHandler(self.sentry_handler)

    def init_console_handler(self):
        self.console_handler = logging.StreamHandler(sys.stdout)
        # hdlr = RobustLogHandler(hdlr)
        self.console_handler.setFormatter(self.verb_log_formatter[self.verbosity])
        self.addHandler(self.console_handler)

    def init_file_handler(self):
        if self.home_dir:
            self.file_handler = logging.FileHandler(self.home_dir + ('%s.log' % self.appName))
        else:
            self.file_handler = logging.FileHandler('/tmp/%s.log' % self.appName)
        # hdlr = RobustLogHandler(hdlr)
        self.file_handler.setFormatter(self.verb_log_formatter[0])
        self.addHandler(self.file_handler)

    def init_syslog_handler(self):
        self.syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL2)
        self.syslog_handler.priority_map["TRACE"] = "debug"
        # hdlr = RobustLogHandler(hdlr)
        self.syslog_handler.setFormatter(self.verb_log_formatter[0])
        self.addHandler(self.syslog_handler)

    def init_custom_handler(self):
        if self.get_custom_handler_function:
            custom_handler = self.get_custom_handler_function()
            if custom_handler:
                self.custom_handler = custom_handler
                # hdlr = RobustLogHandler(hdlr)
                self.custom_handler.setFormatter(self.verb_log_formatter[self.verbosity])
                self.addHandler(self.custom_handler)

    def debug(self, msg, *args, **kwargs):
        if not self.isEnabledFor(logging.DEBUG):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if not self.isEnabledFor(logging.INFO):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if not self.isEnabledFor(logging.WARNING):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if not self.isEnabledFor(logging.ERROR):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if not self.isEnabledFor(logging.CRITICAL):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(logging.CRITICAL, msg, *args, **kwargs)

    def _log_it(self, level, msg, *args, **kwargs):
        extra = kwargs
        extra['appName'] = self.appName
        extra['instanceId'] = self.instanceId
        try:
            frame = sys._getframe(4)
            fn, lno, func, _, _ = inspect.getframeinfo(frame, 1)
            if self.verbosity > 1:
                #Aquellos que usan o pueden usar el nivel 2
                if self.socket_handler or self.console_handler or self.sentry_handler:
                    stack_trace = traceback.extract_stack(f=frame, limit=10)[-3:-1]
                    try:
                        the_class = frame.f_locals["self"].__class__
                        the_class = str(the_class).split(".")[-1]
                    except KeyError:
                        the_class = "<no class>"
                    # code = frame.f_code
                    extra['class'] = "%s" % (the_class,)
                    extra['stack_trace'] = "%s" % (stack_trace,)
                    callargs = inspect.getargvalues(frame)
                    extra['callargs'] = "%s" % (callargs,)
        except BaseException as e:
            fn, lno, func = "(SW LOGGER TB ERROR)", 0, "(SW LOGGER TB ERROR)"
            extra = {}
        try:
            record = self.makeRecord(self.name, level, fn, lno, msg, args, None, func, extra)
            self.handle(record)
        except BaseException as e:
            pre_log("SW LOGGER LOG ERROR", e)

    fatal = critical

    def trace(self, msg, *args, **kwargs):
        if not self.isEnabledFor(TRACE_LVL):
            return
        msg = self._msg_format(msg, *args, **kwargs)
        self._log_it(TRACE_LVL, msg, *args, **kwargs)


class SwSelectiveLogger(SwLogger):
    log_host = None

    @classmethod
    def configure(cls, *args, **kwargs):
        if len(args) != 0 and len(kwargs.items()) != 0:
            raise Exception('No se puede usar invocacion por key y por posicion juntos...')
        more_args, more_kwargs = SwLogger.configure(*args, **kwargs)
        cls.log_host = param_get(more_args, more_kwargs, 0, 'log_host')
        return (more_args[1:], more_kwargs)

    def __init__(self, ip, port, name='', level=TRACE_LVL):
        SwLogger.__init__(self, name, level)
        self.init_socket_handler(ip, port)

    def on_selective_log(self, ip, port):
        self.init_socket_handler(ip, port)

    def off_selective_log(self):
        self.removeHandler(self.socket_handler)
        self.socket_handler = None

    def init_socket_handler(self, ip=None, port=60514):
        assert((type(ip) is str) or (type(ip) is unicode) or (ip is None))
        assert(type(port) is int)
        try:
            if not ip:
                log_host = self.log_host
            elif re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip) is not None:
                assert((type(ip) is str) or (type(ip) is unicode))
                log_host = ip
            else:
                try:
                    log_host = gethostbyname(ip)
                except gaierror as e:
                    pre_log('Cannot init socket handler with given ip', e)
                    log_host = self.log_host
        except AttributeError as e:
            pre_log('Missing config', e)
            return None
        try:
            self.socket_handler = logging.handlers.SocketHandler(host=log_host, port=port)
            # hdlr = RobustLogHandler(hdlr)
            self.socket_handler.setFormatter(self.verb_log_formatter[self.verbosity])
            leastLevel = min(TRACE_LVL, self.level)
            self.socket_handler.setLevel(leastLevel)
            self.addHandler(self.socket_handler)
        except BaseException as e:
            pre_log('Cant init socket handler', e)


class SwLoggerAdapter(logging.LoggerAdapter):
    defaultLogger = DummyObj()

    @classmethod
    def configure(cls, defaultLogger):
        cls.defaultLogger = defaultLogger

    def __init__(self, context=None, logger=None):
        self.context = []
        if context:
            self.context.append(str(context))
        if logger:
            logging.LoggerAdapter.__init__(self, logger, {'context': context})
        else:
            logging.LoggerAdapter.__init__(self, self.defaultLogger, {'context': context})

    def add_context(self, context):
        self.context.append(str(context))

    def pop_context(self):
        return self.context.pop()

    def trace(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.trace(msg, *args, **kwargs)

    def process(self, msg, kwargs):
        more_context = ('|'.join(self.context))
        if "context" in kwargs:
            more_context = kwargs["context"] + more_context
        kwargs["context"] = more_context
        return msg, kwargs
