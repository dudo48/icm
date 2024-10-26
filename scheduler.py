import datetime
import pickle
import sched
import time
from typing import cast

from icm.constants import RUN_FREQUENCY_DAYS
from icm.logger import datetime_format, logger
from icm.path import NEXT_RUN
from main import run_icm


def get_next_run() -> datetime.datetime:
    if not NEXT_RUN.exists():
        return datetime.datetime.now()
    with open(NEXT_RUN, "rb") as file:
        return cast(datetime.datetime, pickle.load(file))


def set_next_run(previous_run: datetime.datetime):
    with open(NEXT_RUN, "wb") as file:
        previous_run = previous_run.replace(microsecond=0)
        pickle.dump(previous_run + datetime.timedelta(hours=RUN_FREQUENCY_DAYS, file)


def run_and_set_next():
    now = datetime.datetime.now()
    run_icm()
    set_next_run(now)


def run_scheduler():
    scheduler = sched.scheduler(time.time, time.sleep)
    while True:
        next_run = get_next_run()
        logger.debug(f"Scheduled to run on {next_run.strftime(datetime_format())}.")
        scheduler.enterabs(next_run.timestamp(), 1, run_and_set_next)
        scheduler.run()


if __name__ == "__main__":
    run_scheduler()
