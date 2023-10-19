#!F:/Programs/Python/Internet Consumption Monitor ICM/venv/Scripts/pythonw.exe

import datetime
import json
import math
import os
import pickle
import time

import paths
import storage
import utility
from constants import HOUR_SECONDS, PROJECT_ROOT
from pytz import timezone

import icm


def run_scheduler():
    log_scheduled_date = True

    while True:
        current_datetime = datetime.datetime.now(timezone('Africa/Cairo'))
        next_datetime = storage.load_next_datetime()

        if not next_datetime or current_datetime >= next_datetime:
            icm.run()  # type: ignore

            next_datetime = current_datetime + datetime.timedelta(days=1)
            storage.save_next_datetime(next_datetime)
            log_scheduled_date = True
        else:
            if log_scheduled_date:
                utility.logger.debug(
                    f"Scheduled to run on {next_datetime.strftime(r'%B %d, %Y, %I:%M %p')}.")
                log_scheduled_date = False
            else:
                utility.logger.debug('Not yet.')

            total_seconds = (next_datetime - current_datetime).total_seconds()

            # sleep for half the duration to counter 'sleep freezing' which happens when the computer sleeps
            sleep_duration = math.ceil(
                total_seconds if total_seconds < HOUR_SECONDS else total_seconds / 2
            )
            time.sleep(sleep_duration)


if __name__ == '__main__':
    run_scheduler()
