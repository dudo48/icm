import datetime
import math
import pickle
import time
from collections.abc import Callable
from typing import TypeVar, cast

from icm.config import config
from icm.logger import datetime_format, logger
from icm.path import NEXT_RUN
from main import run_icm

T = TypeVar("T")

def get_next_run() -> datetime.datetime:
    if not NEXT_RUN.exists():
        return datetime.datetime.now()
    with open(NEXT_RUN, "rb") as file:
        return cast(datetime.datetime, pickle.load(file))


def set_next_run(previous_run: datetime.datetime):
    with open(NEXT_RUN, "wb") as file:
        delta = datetime.timedelta(hours=config["scheduler"]["run_every_hours"])
        pickle.dump(previous_run.replace(microsecond=0) + delta, file)


def run_on(date: datetime.datetime, fun: Callable[[], T], check_every_seconds: float = 3600) -> T:
    """
    Run a function on a specific date and time.

    Args:
        date (datetime.datetime): The date and time to run the function on.
        fun (Callable[[], T]): function to execute.
        check_every_seconds (float, optional): Check if it is time to execute the function every X seconds. Defaults to 3600 (1 hour).

    Returns:
        T: Return value of the scheduled function.
    """
    while True:
        now = datetime.datetime.now()
        if now >= date:
            break
        seconds = math.ceil(min(check_every_seconds, (date - now).total_seconds()))
        logger.debug(f"Not yet, checking again in {datetime.timedelta(seconds=seconds)}.")
        time.sleep(seconds)
    return fun()


def run_scheduler():
    while True:
        next_run = get_next_run()
        logger.debug(f"Scheduled to run on {next_run.strftime(datetime_format())}.")
        run_on(
            next_run,
            lambda: set_next_run(run_icm().date),
            config["scheduler"]["check_every_hours"] * 3600,
        )


if __name__ == "__main__":
    run_scheduler()
