import time


# selenium send keys but with a delay
def type_slowly(element, text):
    for char in text:
        time.sleep(0.1)
        element.send_keys(char)


# convert all list elements to string
def string_list(original_list):
    return [str(element) for element in original_list]
