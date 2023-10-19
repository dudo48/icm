import logging
import os
import time

import paths
from constants import PROJECT_ROOT, TYPE_SLOWLY_DELAY


# selenium send keys but with a delay
def type_slowly(element, text):
    for c in text:
        time.sleep(TYPE_SLOWLY_DELAY)
        element.send_keys(c)
        time.sleep(TYPE_SLOWLY_DELAY)


# convert dict values to string-only list
def dict_to_str_list(dictionary):
    return [str(element) for element in dictionary.values()]


# attaches and configures the handlers for the logger
def configure_logger():
    logger.setLevel(logging.DEBUG)

    logger_formatter = logging.Formatter(
        "[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.DEBUG)
    console_handle.setFormatter(logger_formatter)

    os.makedirs(os.path.dirname(paths.log), exist_ok=True)
    file_handle = logging.FileHandler(paths.log, 'w')
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(logger_formatter)

    logger.addHandler(console_handle)
    logger.addHandler(file_handle)


# configure logger
logger = logging.getLogger(__name__)
configure_logger()
