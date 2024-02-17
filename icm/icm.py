import os
import subprocess
import sys

import paths
import storage
from constants import REMAINING_DAYS_ALERT_MARGIN, REMAINING_UNITS_ALERT_MARGIN
from logger import logger
from scraper import Scraper


def send_message(message):
    return subprocess.Popen(['notify-send', 'Internet Consumption Manager', message])

def run():
    args = sys.argv[1:]
    debug_mode = '--debug' in args

    logger.debug("Running ICM...")
    scraper = None
    try:
        logger.debug("Opening browser...")
        scraper = Scraper(debug_mode=debug_mode)

        logger.debug("Logging in...")
        scraper.login()

        logger.debug("Scraping data...")
        previous_record = storage.get_previous_record()
        record = scraper.create_record(previous_record)

        logger.debug("Adding data to databases...")

        # convert all data to string for consistent manifestation
        data_list = [str(e) for e in record.values()]
        storage.create_report(data_list)

        # do not affect databases when debugging
        if not debug_mode:
            storage.add_to_sql_database(data_list)
            storage.add_to_csv_database(data_list)
            storage.set_previous_record(record)

        # logging warnings
        warnings = []

        if record['days_left'] < REMAINING_DAYS_ALERT_MARGIN and (not previous_record or previous_record['days_left'] > REMAINING_DAYS_ALERT_MARGIN):
            warnings.append(
                f'WARNING: Only {record["days_left"]} days left. Remember to recharge your internet')
        if record['remaining_units'] < REMAINING_UNITS_ALERT_MARGIN and (not previous_record or previous_record['remaining_units'] > REMAINING_UNITS_ALERT_MARGIN):
            warnings.append(
                f'WARNING: Only {record["remaining_units"]} internet units left. Remember to recharge your internet')

        for warning in warnings:
            logger.debug(warning)
            send_message(warning)
        logger.debug("Task completed successfully.")

    except BaseException as error:
        message = f'ICM run failed: {error}'
        logger.debug(message)
        send_message(message)
    finally:
        if scraper:
            scraper.browser.quit()


if __name__ == '__main__':
    run()
