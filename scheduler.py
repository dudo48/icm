import datetime
import math
import pickle
import time
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from icm.config import config
from icm.database import SessionMaker
from icm.logger import logger, notify
from icm.models import State
from icm.utility import DATETIME_FORMAT
from main import run_icm

T = TypeVar("T")


def get_state(session: Session, key: str, default: Any) -> Any:
    state = session.scalars(select(State).where(State.key == key)).first()
    return state.loaded_value if state else default


def set_state(session: Session, key: str, value: Any):
    session.merge(State(key=key, value=pickle.dumps(value)))


def run_on(fun: Callable[[], T], date: datetime.datetime, check_every: datetime.timedelta) -> T:
    """
    Run a function on a specific date and time.

    Args:
        date (datetime.datetime): The date and time to run the function on.
        fun (Callable[[], T]): function to execute.
        check_every (datetime.timedelta): The time to wait before checking if it is time to execute the function.

    Returns:
        T: Return value of the scheduled function.
    """
    while True:
        now = datetime.datetime.now()
        if now >= date:
            break
        min_delta = datetime.timedelta(seconds=math.ceil(min(check_every, date - now).total_seconds()))
        logger.debug(f"Not yet, checking again in {min_delta}.")
        time.sleep(min_delta.total_seconds())
    return fun()


def run_scheduler():
    def _run_icm():
        with SessionMaker() as session:
            total_retries: int = config["scheduler"]["retries"]
            retries_left: int = get_state(session, "retries_left", total_retries)
            new_retries_left = total_retries
            next_run_delta = datetime.timedelta(hours=config["scheduler"]["run_every_hours"])
            if retries_left >= 0:
                try:
                    run_icm(session)
                except Exception as e:
                    if retries_left == 0:
                        logger.debug("No more retries left. Skipping this run...")
                        notify(str(e))
                    else:
                        next_run_delta = datetime.timedelta(minutes=config["scheduler"]["retry_every_minutes"])
                        new_retries_left = retries_left - 1
                        logger.debug(f"{retries_left} {'retry' if retries_left == 1 else 'retries'} left.")
            set_state(session, "retries_left", new_retries_left)
            set_state(session, "next_run", datetime.datetime.now() + next_run_delta)
            session.commit()

    while True:
        with SessionMaker() as session:
            next_run: datetime.datetime = get_state(session, "next_run", datetime.datetime.now())
        logger.debug(f"Scheduled to run on {next_run.strftime(DATETIME_FORMAT)}.")
        run_on(_run_icm, next_run, datetime.timedelta(hours=config["scheduler"]["check_every_hours"]))


if __name__ == "__main__":
    run_scheduler()
