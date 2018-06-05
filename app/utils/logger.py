import pendulum
import socket
import logging

from pythonjsonlogger import jsonlogger
from sanic.log import LOGGING_CONFIG_DEFAULTS
from logzero import setup_logger
from collections import OrderedDict

# https://github.com/madzak/python-json-logger
class CustomFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomFormatter, self).add_fields(log_record, record, message_dict)
        log_record["timestamp"] = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss z")

        if not log_record.get("levelname"):
            log_record["levelname"] = record.levelname.upper()

        # if it's a custom log, log the file that created it
        if not record.name in ["root", "sanic.access", "sanic.error"]:
            log_record["name"] = f"{record.name}"

        # Additional debug info
        if log_record["levelname"] == "DEBUG":
            log_record["name"] = f"{record.filename}:{record.lineno}"

    def process_log_record(self, log_record):
        super(CustomFormatter, self).process_log_record(log_record)
        tmp_log = {}
        for k, v in log_record.items():
            # makes HTTP requests easier to parse and filter
            if k == "request" and v:
                req = v.split(" ")
                tmp_log["method"] = req[0]
                tmp_log["url"] = req[1]
            # better hostname matching than default
            elif k == "host" and v:
                tmp_log["host"] = socket.getfqdn()
            # if no specific processing, include if the value is not null
            elif v:
                tmp_log[k] = v
        # alphabetically sort the log. JsonFormatter expects OrderedDict.
        return OrderedDict(sorted(tmp_log.items()))


# Overwriting Sanic's default logging formatters.
# https://github.com/channelcat/sanic/blob/master/sanic/log.py
def get_sanic_log_config():
    log_format = (
        "(%(name)s)[%(levelname)s][%(host)s]: %(request)s %(message)s %(status)d"
    )
    log_config_overrides = {
        "formatters": {
            "access": {"format": log_format, "class": "utils.logger.CustomFormatter"},
            "generic": {"format": log_format, "class": "utils.logger.CustomFormatter"},
        }
    }

    return {**LOGGING_CONFIG_DEFAULTS, **log_config_overrides}


def get_logger(filename):
    return setup_logger(name=filename, formatter=CustomFormatter())
