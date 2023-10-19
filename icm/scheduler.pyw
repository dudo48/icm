#!F:/Programs/Python/Internet Consumption Monitor ICM/venv/Scripts/pythonw.exe

import datetime
import json
import pickle
import time

import utility
from pytz import timezone

import icm
from icm.constants import CHECK_INTERVAL_FACTOR, MIN_CHECK_INTERVAL


def load_next_datetime() -> datetime.datetime | None:
    try:
        with open("../persistent/next_datetime", 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


def save_next_datetime(next_datetime):
    with open("../persistent/next_datetime", 'wb') as file:
        return pickle.dump(next_datetime, file)


def check():
    current_datetime = datetime.datetime.now(timezone('Africa/Cairo'))
    next_datetime = load_next_datetime()

    if not next_datetime or current_datetime >= next_datetime:
        icm.run()  # type: ignore

        next_datetime = current_datetime + datetime.timedelta(days=1)
        save_next_datetime(next_datetime)
        utility.logger.debug(
            f"Scheduled to run on {next_datetime.strftime(r'%B %d, %Y, %I:%M %p')}.")
    else:
        seconds_remaining = (next_datetime - current_datetime).total_seconds()
        sleep_duration = max(
            seconds_remaining * CHECK_INTERVAL_FACTOR,
            MIN_CHECK_INTERVAL
        )
        time.sleep(sleep_duration)


if __name__ == '__main__':
    while True:
        check()
