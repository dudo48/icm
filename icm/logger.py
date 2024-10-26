import datetime
import logging

from pytz import timezone

from icm import path
from icm.constants import TIMEZONE


def datetime_format() -> str:
    return "%Y-%m-%d %I:%M:%S %p"


# to set the logger to a custom timezone
def converter(*_):
    return datetime.datetime.now(timezone(TIMEZONE)).timetuple()


# attaches and configures the handlers for the logger
def configure_logger():
    logging.Formatter.converter = converter

    logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter("[%(asctime)s] %(message)s", datetime_format())

    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.DEBUG)
    console_handle.setFormatter(logger_formatter)

    file_handle = logging.FileHandler(path.LOG, "w")
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(logger_formatter)

    logger.addHandler(console_handle)
    logger.addHandler(file_handle)


logger = logging.getLogger(__name__)
configure_logger()
