import logging
import subprocess

from icm import path
from icm.utility import DATETIME_FORMAT


def notify(message: str):
    return subprocess.Popen(["notify-send", "Internet Consumption Manager", message])


# attaches and configures the handlers for the logger
def configure_logger():
    logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter("[%(asctime)s] %(message)s", DATETIME_FORMAT)

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
