import logging
from gunicorn import glogging

# from pythonjsonlogger import jsonlogger


def create_logger(name):
    logger = logging.getLogger(name)
    # syslog = logging.StreamHandler()
    # formatter = jsonlogger.JsonFormatter()
    # syslog.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    # logger.addHandler(syslog)

    return logger


# disable default logging; stdout from logging middleware is captured by supervisord and written to file
class GunicornJSONLogger(glogging.Logger):
    def setup(self, cfg):
        self.error_handlers = []
        self.access_handlers = []
        self.error_logger = None
        self.access_logger = None
