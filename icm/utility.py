import time
import logging


# selenium send keys but with a delay
def type_slowly(element, text):
    for char in text:
        time.sleep(0.1)
        element.send_keys(char)
        time.sleep(0.1)


# convert dict values to string-only list
def dict_to_str_list(dictionary):
    return [str(element) for element in dictionary.values()]


# attaches and configures the handlers for the logger
def configure_logger():
    logger.setLevel(logging.DEBUG)

    logger_formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.DEBUG)
    console_handle.setFormatter(logger_formatter)

    file_handle = logging.FileHandler("../log.txt", 'w')
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(logger_formatter)

    logger.addHandler(console_handle)
    logger.addHandler(file_handle)


# configure logger
logger = logging.getLogger(__name__)
configure_logger()
