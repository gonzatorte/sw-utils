import logging
import logging.handlers
import sys
import threading
from sw_utils.dummy_obj import DummyObj
from sw_utils.logs.logger import SwLogger, SwSelectiveLogger, SwLoggerAdapter
from sw_utils.logs.constants import TRACE_LVL
from sw_utils.logs.utils import pre_log


t_data = threading.local()
#ToDo: Poner un parche en el getattr de este metodo para que retorne un objeto por defecto en algunos casos.
# Por compatibilidad con los test_cases
def set_thread_logger(logger):
    t_data.logger = logger


def get_thread_logger():
    return getattr(t_data, 'logger', None)


# _________________ NIVELES DE LOG
# CRITICAL 	50
# ERROR 	40
# WARNING 	30
# INFO 	    20
# TRACE     15
# DEBUG 	10
# NOTSET 	0
logging.addLevelName(TRACE_LVL, 'TRACE')


def _decide_main_logger():
    logger = getattr(t_data, 'logger', None)
    return logger or rootAdapter

def log_fatal(*args, **kwargs):
    if _inited:
        _decide_main_logger().critical(*args, **kwargs)

def log_alert(*args, **kwargs):
    if _inited:
        _decide_main_logger().critical(*args, **kwargs)

def log_critical(*args, **kwargs):
    if _inited:
        _decide_main_logger().critical(*args, **kwargs)

def log_error(*args, **kwargs):
    if _inited:
        _decide_main_logger().error(*args, **kwargs)

def log_warning(*args, **kwargs):
    if _inited:
        _decide_main_logger().warning(*args, **kwargs)

def log_info(*args, **kwargs):
    if _inited:
        _decide_main_logger().info(*args, **kwargs)

def log_trace(*args, **kwargs):
    if _inited:
        _decide_main_logger().trace(*args, **kwargs)

def log_debug(*args, **kwargs):
    if _inited:
        _decide_main_logger().debug(*args, **kwargs)

def get_current_logger():
    if _inited:
        return _decide_main_logger()
    else:
        return DummyObj()


rootLogger = None
rootAdapter = None
_appName = None
_inited = False


def _dummy_log_init():
    # Aca debe crear las variables de ambiente para que funcione usando cosas dummy
    pass


_dummy_log_init()


def log_init_django(appName_, custom_handler_getter=None):
    from django.conf import settings
    aws = getattr(settings, 'AWS_ENV', None)
    log_lvl = int(settings.LOG_LEVEL)
    log_host = settings.LOG_HOST
    log_verb = int(settings.LOG_VERBOSITY)
    home_dir = getattr(settings, 'LOG_HOMEDIR', '/tmp/')
    log_init_manual(appName_, home_dir, custom_handler_getter, aws, log_verb, log_lvl, log_host)


log_init = log_init_django


def log_init_manual(appName, home_dir, custom_handler_getter, aws, log_verb, log_lvl, log_host):
    thismodule = sys.modules[__name__]
    is_inited = getattr(thismodule, '_inited', None)
    if is_inited:
        return
    try:
        setattr(thismodule, '_appName', appName)

        format_0 = "[%(appName)s]: %(asctime)s " \
                   "[%(instanceId)s][%(processName)s:%(process)s][%(threadName)s:%(thread)s][%(levelname)s:%(levelno)s]" \
                   "[%(context)s]"
        format_1 = "{1| %(filename)s:%(lineno)d %(module)s:%(funcName)s |1}"
        format_2 = "{2| %(stack_trace)s %(callargs)s |2}"

        verb_log_formatter = [
            logging.Formatter(format_0 + " <%(message)s>"),
            logging.Formatter(format_0 + format_1 + " <%(message)s>"),
            logging.Formatter(format_0 + format_1 + format_2 + " <%(message)s>")
        ]

        instanceId = 'No'
        if aws:
            instanceId = '<UNKNOWN>'
            try:
                import boto.utils
                identity_document = boto.utils.get_instance_identity()['document']
                instanceId = identity_document['instanceId']
            except BaseException as e:
                pre_log("Cannot get all AWS info", e)

        SwLogger.configure(aws, instanceId, verb_log_formatter, log_verb, custom_handler_getter, appName, home_dir)
        SwSelectiveLogger.configure(aws, instanceId, verb_log_formatter, log_verb, custom_handler_getter, appName, home_dir, log_host)

        rootLogger_ = SwLogger(name=appName)
        rootLogger_.setLevel(logging.DEBUG)
        log_level = log_lvl or logging.DEBUG
        rootLogger_.setLevel(log_level)

        SwLoggerAdapter.configure(defaultLogger=rootLogger_)
        setattr(thismodule, 'rootLogger', rootLogger_)
        setattr(thismodule, 'rootAdapter', SwLoggerAdapter(logger=rootLogger_))

        if aws:
            pass

    except BaseException as e:
        pre_log('Error at inicializing logger module', e)
        raise
    else:
        setattr(thismodule, '_inited', True)


def push_context(context):
    l = get_thread_logger()
    if l:
        l.add_context(context)


def pop_context(context):
    l = get_thread_logger()
    if l:
        return l.pop_context()


def log_shutdown():
    logging.shutdown()
    thismodule = sys.modules[__name__]
    setattr(thismodule, '_inited', False)


def get_root_logger():
    if not _inited:
        return DummyObj()
    return rootLogger


selective_loggers = {}


def get_selective_logger(ip, port):
    if not _inited:
        return DummyObj()
    try:
        s_logger = selective_loggers[(ip, port)]
    except KeyError:
        s_logger = SwSelectiveLogger(ip=ip, port=port)
        s_logger = SwLoggerAdapter(logger=s_logger)
        selective_loggers[(ip, port)] = s_logger
    return s_logger


def log_exceptions(function):
    def decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except BaseException as e:
            log_error(e)
            raise
    return decorator
