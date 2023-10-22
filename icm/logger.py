import datetime
import logging
import os
import time

import paths
from constants import PROJECT_ROOT, TIMEZONE
from pytz import timezone


# to set the logger to a custom timezone
def converter(*args):
    return datetime.datetime.now(timezone(TIMEZONE)).timetuple()


# attaches and configures the handlers for the logger
def configure_logger():
    logging.Formatter.converter = converter

    logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter(
        "[%(asctime)s] %(message)s", "%Y-%m-%d %I:%M:%S %p")

    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.DEBUG)
    console_handle.setFormatter(logger_formatter)

    os.makedirs(os.path.dirname(paths.log), exist_ok=True)
    file_handle = logging.FileHandler(paths.log, 'w')
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(logger_formatter)

    logger.addHandler(console_handle)
    logger.addHandler(file_handle)


logger = logging.getLogger(__name__)
configure_logger()
