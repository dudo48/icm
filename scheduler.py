import datetime
import math
import time
from collections.abc import Callable
from typing import TypeVar, cast

from sqlalchemy import func, select

from icm.utility import DATETIME_FORMAT
from icm.config import config
from icm.database import Session
from icm.logger import logger, notify
from icm.record import Record
from main import run_icm

T = TypeVar("T")


def get_next_run() -> datetime.datetime:
    delta = datetime.timedelta(hours=config["scheduler"]["run_every_hours"])
    with Session() as session:
        record = session.scalars(
            select(Record).where(
                Record.date == select(func.max(Record.date)).scalar_subquery()
            )
        ).first()
        if record:
            return record.date + delta
        return datetime.datetime.now()


def run_on(fun: Callable[[], T], date: datetime.datetime, check_every_seconds: float = 3600) -> T:
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


def try_to_run(fun: Callable[[], T], retries: int, retry_every_seconds: float = 60) -> T:
    """
    Call a function. Retrying multiple times if it raises an exception until it succeeds.

    Args:
        fun (Callable[[], T]): The function to call which might throw an exception.
        retries (int, optional): Number of times to try to call the function (the first call is not calculated).
        retry_every_seconds (float, optional): The number of seconds to sleep between each retry call. Defaults to 60.

    Returns:
        T: The return value of the function
    """
    result = None
    for retry in range(retries + 1):
        try:
            result = fun()
            break
        except Exception as e:
            if retry >= retries:
                notify(str(e))
                raise
            else:
                logger.debug(f"{retries - retry} {'retry' if retries - retry == 1 else 'retries'} left.")
                logger.debug(f"Trying again in {datetime.timedelta(seconds=retry_every_seconds)}.")
                time.sleep(retry_every_seconds)
    return cast(T, result)


def run_scheduler():
    def _run_icm():
        return try_to_run(
            run_icm,
            config["scheduler"]["retries"],
            config["scheduler"]["retry_every_minutes"] * 60,
        )

    while True:
        next_run = get_next_run()
        logger.debug(f"Scheduled to run on {next_run.strftime(DATETIME_FORMAT)}.")
        run_on(_run_icm, next_run, config["scheduler"]["check_every_hours"] * 3600)


if __name__ == "__main__":
    run_scheduler()
