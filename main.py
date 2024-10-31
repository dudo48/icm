import subprocess
import traceback

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from sqlalchemy import select

from icm.config import config
from icm.database import Session
from icm.logger import logger
from icm.path import REPORT
from icm.record import Record
from icm.scraper import login


def send_message(message: str):
    return subprocess.Popen(["notify-send", "Internet Consumption Manager", message])


def check_warnings(record: Record):
    warnings: list[str] = []
    if record.days_left < config["warning"]["remaining_days"]:
        warnings.append(
            f"Only {record.days_left} days left. Remember to recharge your internet"
        )
    if record.remaining_units < config["warning"]["remaining_units"]:
        warnings.append(
            f"Only {record.remaining_units} internet units left. Remember to recharge your internet"
        )

    for warning in warnings:
        logger.debug(warning)
        send_message(warning)


def create_report():
    logger.debug("Creating report...")
    with Session() as session:
        latest_records = session.scalars(select(Record).order_by(Record.date.desc()).limit(5))
        with open(REPORT, "w") as file:
            file.write("\n\n".join([str(record) for record in latest_records]))


def run_icm(headless: bool = True):
    try:
        with login(headless=headless) as scraper, Session() as session:
            record = scraper.create_record()
            logger.debug("Adding record to database...")
            session.add(record)
            session.commit()
            check_warnings(record)
        create_report()
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Element not found, {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    run_icm()
