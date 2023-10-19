import json
import os
import sqlite3

import utility

from icm.constants import DELIMITER, PROJECT_ROOT, TABLE_HEADERS


def add_to_csv_database(record):
    # convert to one line separated by delimiter
    record_list = DELIMITER.join(utility.dict_to_str_list(record))
    path = os.path.join(PROJECT_ROOT, '/databases/database.csv')
    with open(path, mode='a') as file:
        file.write('\n' + record_list)


def add_to_sql_database(record):
    # make all elements of type 'string'
    record_list = utility.dict_to_str_list(record)

    path = os.path.join(PROJECT_ROOT, '/databases/database.db')
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO InternetConsumption VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record_list))
    conn.commit()
    conn.close()


def create_report(record):
    record_list = utility.dict_to_str_list(record)
    path = os.path.join(PROJECT_ROOT, '/debug/report.txt')
    with open(path, 'w') as file:
        for i in range(len(TABLE_HEADERS)):
            file.write("{:<40}{}\n".format(
                TABLE_HEADERS[i] + ':', record_list[i]))  # aligned lines


# saves current record to previous_record file
def set_previous_record(record):
    path = os.path.join(PROJECT_ROOT, '/temp/previous_record.json')
    with open(path, 'w') as file:
        json.dump(record, file, indent=4)


def get_previous_record():
    path = os.path.join(PROJECT_ROOT, '/temp/previous_record.json')
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
