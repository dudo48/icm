import datetime
from typing import Iterable

from sqlalchemy import select

from icm.config import config
from icm.database import Session
from icm.logger import logger, notify
from icm.path import REPORT
from icm.record import Record
from icm.scraper import logged_in_scraper


def check_warnings(record: Record):
    warnings: list[str] = []
    time_left = record.renewal_date - record.date
    if time_left < datetime.timedelta(days=config["warning"]["remaining_days"]):
        warnings.append(
            f"Only {time_left} left. Remember to recharge your internet."
        )
    if record.remaining_units < config["warning"]["remaining_units"]:
        warnings.append(
            f"Only {record.remaining_units} internet units left. Remember to recharge your internet."
        )

    for warning in warnings:
        logger.debug(warning)
        notify(warning)


def create_report(records: Iterable[Record]):
    with open(REPORT, "w") as file:
        file.write("\n\n".join([str(record) for record in records]))


def run_icm(headless: bool = True):
    try:
        with logged_in_scraper(headless=headless) as scraper, Session() as session:
            new_record = scraper.create_record()
            check_warnings(new_record)
            logger.debug("Adding record to database...")
            session.add(new_record)
            session.commit()
            logger.debug("Creating report...")
            create_report(session.scalars(select(Record).order_by(Record.date.desc()).limit(5)))
            return new_record
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == "__main__":
    run_icm()
