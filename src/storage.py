import pickle
import sqlite3
from src import constants, utility


def add_to_csv_database(record):
    record = constants.DELIMITER.join(utility.string_list(record))  # convert to one line separated by delimiter
    with open("../databases/database.csv", mode='a') as file:
        file.write('\n' + record)
        file.close()


def add_to_sql_database(record):
    record = utility.string_list(record)  # make all elements of type 'string'
    conn = sqlite3.connect("../databases/database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO InternetConsumption VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record))
    conn.commit()
    conn.close()


def create_report(record):
    record = utility.string_list(record)
    with open("../report.txt", mode='w') as file:
        for i in range(len(constants.TABLE_HEADERS)):
            file.write("{:<40}{}\n".format(constants.TABLE_HEADERS[i] + ':', record[i]))  # aligned lines
        file.close()


# saves current record to previous_record file
def set_previous_record(record):
    with open("../persistent/previous_record", 'wb') as file:
        pickle.dump(record, file)
