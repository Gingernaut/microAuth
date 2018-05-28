import pendulum
from pythonjsonlogger import jsonlogger
from sanic.log import LOGGING_CONFIG_DEFAULTS
from logzero import setup_logger


def get_sanic_log_config():
    log_config_overrides = {
        "formatters": {
            "access": {
                "format": "%(asctime)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
            "generic": {
                "format": "%(asctime)s %(levelname)s %(host)s %(status)d %(request)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        }
    }

    return {**LOGGING_CONFIG_DEFAULTS, **log_config_overrides}


def get_logger(filename):
    class CustomFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomFormatter, self).add_fields(log_record, record, message_dict)
            log_record["filename"] = str(filename)
            if not log_record.get("asctime"):
                log_record["timestamp"] = pendulum.now().format(
                    "YYYY-MM-DD HH:mm:ss ZZ"
                )
            if log_record.get("level"):
                log_record["level"] = log_record["level"].upper()
            else:
                log_record["level"] = record.levelname

    return setup_logger(str(filename), formatter=CustomFormatter())
