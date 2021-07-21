import sys
import time
import logging


# configure logger
logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filename="../log.txt",
                    filemode='w')


# selenium send keys but with a delay
def type_slowly(element, text):
    for char in text:
        time.sleep(0.1)
        element.send_keys(char)
        time.sleep(0.1)


# convert all list elements to string
def string_list(original_list):
    return [str(element) for element in original_list]
