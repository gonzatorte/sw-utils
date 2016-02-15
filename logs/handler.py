import logging


class RobustLogHandler(logging.Handler):
    def __init__(self, hand):
        logging.Handler.__init__(self)
        self.wrapper = hand

    def emit(self, record):
        try:
            self.wrapper.emit(record)
        except:
            pass

    def handleError(self, record):
        pass


# class SwSyslogHandler(logging.handlers.SysLogHandler):
#     # Sino probar inyectarle es mapeo este a huevo
#     priority_map = {
#         "DEBUG": "debug",
#         "TRACE": "debug",
#         "INFO": "info",
#         "WARNING": "warning",
#         "ERROR": "error",
#         "CRITICAL": "critical"
#     }
#
#     def __init__(self, address, facility, socktype=None):
#         logging.handlers.SysLogHandler.__init__(self, address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL2, socktype=socktype)
