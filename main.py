import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from icm import reporter
from icm.config import config
from icm.database import SessionMaker
from icm.logger import logger, notify
from icm.models import Record
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


def run_icm(session: Session, headless: bool = True):
    try:
        with logged_in_scraper(headless=headless) as scraper:
            new_record = scraper.create_record()
            check_warnings(new_record)
            session.add(new_record)
            session.flush()
            logger.debug("Record created successfully...")

            package_records = session.scalars(select(Record).where(Record.renewal_date == new_record.renewal_date))
            dataframe = reporter.get_dataframe(package_records)
            logger.debug("Creating report...")
            reporter.save_table(dataframe)
            logger.debug("Creating visual report...")
            reporter.save_plot(dataframe)

            return new_record
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == "__main__":
    with SessionMaker() as session:
        logger.debug(run_icm(session))
        session.rollback()
        logger.debug("Record was not added to database...")
