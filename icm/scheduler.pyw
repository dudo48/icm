#!F:/Programs/Python/Internet Consumption Monitor ICM/venv/Scripts/pythonw.exe

import datetime
import math
import time

from pytz import timezone

import icm
import storage
from constants import (MAX_SLEEP_DURATION, SLEEP_DURATION_LIMIT,
                       TIMEZONE, RUN_INTERVAL_DAYS)
from logger import logger


def compute_sleep_duration(current_datetime, next_datetime):
    total_seconds = (next_datetime - current_datetime).total_seconds()

    # sleep for half the duration to counter 'sleep freezing' which happens when the computer sleeps
    sleep_duration = math.ceil(
        total_seconds if total_seconds < SLEEP_DURATION_LIMIT else total_seconds / 2
    )

    return min(sleep_duration, MAX_SLEEP_DURATION)


def run_scheduler():
    log_scheduled_date = True
    next_datetime = storage.load_next_datetime()

    while True:
        current_datetime = datetime.datetime.now(timezone(TIMEZONE))
        if not next_datetime or current_datetime >= next_datetime:
            icm.run()  # type: ignore

            next_datetime = current_datetime + datetime.timedelta(days=RUN_INTERVAL_DAYS)
            storage.save_next_datetime(next_datetime)
            log_scheduled_date = True
        else:
            sleep_duration = compute_sleep_duration(
                current_datetime, next_datetime)
            if log_scheduled_date:
                logger.debug(
                    f"Scheduled to run on {next_datetime.strftime(r'%B %d, %Y %I:%M:%S %p')}.")
                log_scheduled_date = False

            check_timedelta = datetime.timedelta(seconds=sleep_duration)
            check_datetime = current_datetime + \
                             datetime.timedelta(seconds=sleep_duration)
            logger.debug(
                f"Checking again in {check_timedelta} ({check_datetime.strftime(r'%B %d, %Y %I:%M:%S %p')}).")
            time.sleep(sleep_duration)


if __name__ == '__main__':
    run_scheduler()
