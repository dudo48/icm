import sqlite3
import constants
import utility
import json


def add_to_csv_database(record):
    record_list = constants.DELIMITER.join(utility.dict_to_str_list(record))  # convert to one line separated by delimiter
    with open("../databases/database.csv", mode='a') as file:
        file.write('\n' + record_list)


def add_to_sql_database(record):
    record_list = utility.dict_to_str_list(record)  # make all elements of type 'string'
    conn = sqlite3.connect("../databases/database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO InternetConsumption VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record_list))
    conn.commit()
    conn.close()


def create_report(record):
    record_list = utility.dict_to_str_list(record)
    with open("../report.txt", mode='w') as file:
        for i in range(len(constants.TABLE_HEADERS)):
            file.write("{:<40}{}\n".format(constants.TABLE_HEADERS[i] + ':', record_list[i]))  # aligned lines


# saves current record to previous_record file
def set_previous_record(record):
    with open("../persistent/previous_record.json", 'w') as file:
        json.dump(record, file, indent=4)


def get_previous_record():
    try:
        with open("../persistent/previous_record.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
