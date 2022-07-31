import datetime
import json
import time
import main
import constants
import utility


def get_previous_record_date():
    try:
        with open("../persistent/previous_record_datetime.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def set_previous_record_date(data):
    with open("../persistent/previous_record_datetime.json", 'w') as file:
        return json.dump(data, file, indent=4)


def run():
    while True:
        current_datetime = datetime.datetime.now()
        previous_date_json = get_previous_record_date()

        if previous_date_json:
            previous_datetime = datetime.datetime.fromisoformat(previous_date_json['iso'])
            next_run_date = current_datetime.date()
            if next_run_date == previous_datetime.date():
                next_run_date += datetime.timedelta(days=1)

            # datetime objects for next run times(runs in range of start and end only once)
            next_run_start = datetime.datetime.combine(next_run_date, constants.START_HOUR)
            next_run_end = datetime.datetime.combine(next_run_date, constants.END_HOUR)

        if not previous_date_json or next_run_start <= current_datetime <= next_run_end:
            main.run()
            set_previous_record_date({'iso': current_datetime.isoformat()})
        else:
            utility.logger.debug("Not yet.")
            time.sleep(constants.SCHEDULER_CHECK_INTERVAL)


if __name__ == '__main__':
    run()
