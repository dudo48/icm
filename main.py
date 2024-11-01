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


def run_icm(headless: bool = True):
    try:
        with login(headless=headless) as scraper, Session() as session, open(REPORT, "w") as report_file:
            new_record = scraper.create_record()
            logger.debug("Adding record to database...")
            session.add(new_record)
            session.commit()
            logger.debug("Creating report...")
            latest_records = session.scalars(select(Record).order_by(Record.date.desc()).limit(5))
            report_file.write("\n\n".join([str(record) for record in latest_records]))
            check_warnings(new_record)
            return new_record
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Element not found, {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    run_icm()
