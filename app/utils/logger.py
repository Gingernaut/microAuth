import logging
import sys


def get_logger(filename):
    logger = logging.getLogger(str(filename))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    # logger.info(
    #     "test log statement", extra={"props": {"extra_property": "extra_value"}}
    # )

    return logger
