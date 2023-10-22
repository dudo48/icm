import datetime
import json
import os
import pickle
import sqlite3

import paths
from constants import CSV_DELIMITER, PROJECT_ROOT, TABLE_HEADERS


def load_next_datetime() -> datetime.datetime | None:
    try:
        with open(paths.next_datetime, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


def save_next_datetime(next_datetime):
    os.makedirs(os.path.dirname(paths.next_datetime), exist_ok=True)
    with open(paths.next_datetime, 'wb') as file:
        return pickle.dump(next_datetime, file)


def add_to_csv_database(record):
    os.makedirs(os.path.dirname(paths.csv_database), exist_ok=True)
    with open(paths.csv_database, mode='a') as file:
        file.write('\n' + CSV_DELIMITER.join(record))


def add_to_sql_database(record):
    # make all elements of type 'string'
    os.makedirs(os.path.dirname(paths.sql_database), exist_ok=True)
    conn = sqlite3.connect(paths.sql_database)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO InternetConsumption VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record))
    conn.commit()
    conn.close()


def create_report(record):
    os.makedirs(os.path.dirname(paths.report), exist_ok=True)
    with open(paths.report, 'w') as file:
        for i in range(len(TABLE_HEADERS)):
            file.write("{:<40}{}\n".format(
                TABLE_HEADERS[i] + ':', record[i]))  # aligned lines


# saves current record to previous_record file
def set_previous_record(record):
    os.makedirs(os.path.dirname(paths.previous_record), exist_ok=True)
    with open(paths.previous_record, 'w') as file:
        json.dump(record, file, indent=4)


def get_previous_record():
    try:
        with open(paths.previous_record, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
