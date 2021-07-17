import time


def type_slowly(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(0.1)
