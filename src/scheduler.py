import datetime
import os
import pickle
import time
import main
import constants


def get_previous_record_datetime():
    with open("../persistent/previous_record_datetime", 'rb') as date_file:
        return pickle.load(date_file)


def set_previous_record_datetime(value):
    with open("../persistent/previous_record_datetime", 'wb') as datetime_file:
        return pickle.dump(value, datetime_file)


def run():
    while True:
        print(os.getcwd())
        current_datetime = datetime.datetime.now()
        previous_datetime = get_previous_record_datetime()

        next_run_date = current_datetime.date()
        if next_run_date == previous_datetime.date():
            next_run_date += datetime.timedelta(days=1)

        # datetime objects for next run times(runs in range of start and end only once)
        next_run_start = datetime.datetime.combine(next_run_date, constants.START_HOUR)
        next_run_end = datetime.datetime.combine(next_run_date, constants.END_HOUR)

        if next_run_start <= current_datetime <= next_run_end:
            print("Running ICM...")
            exit_code = main.run()
            if exit_code == 0:
                set_previous_record_datetime(current_datetime)
                print("New record successfully created.")
            elif exit_code == 1:
                print("Error.")
        else:
            seconds_to_sleep = (next_run_start - current_datetime).total_seconds()
            print(f"{round(seconds_to_sleep / 3600, 2)} hour(s) till next ICM run.")
            time.sleep(seconds_to_sleep)


if __name__ == '__main__':
    run()
