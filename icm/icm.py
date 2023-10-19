import ctypes
import os
import sys
import time

import storage
import utility
from scraper import Scraper

from icm.constants import (REMAINING_DAYS_ALERT_MARGIN,
                           REMAINING_UNITS_ALERT_MARGIN)


def run():
    args = sys.argv[1:]
    debug_mode = '--debug' in args

    utility.logger.debug("Running ICM...")
    scraper = None
    try:
        utility.logger.debug("Opening browser...")
        scraper = Scraper(debug_mode=debug_mode)

        utility.logger.debug("Logging in...")
        scraper.login()

        utility.logger.debug("Scraping data...")
        record = scraper.create_record()

        utility.logger.debug("Adding data to databases...")
        storage.add_to_sql_database(record)
        storage.add_to_csv_database(record)
        storage.create_report(record)
        storage.set_previous_record(record)

        # logging warnings
        warnings = []
        remaining_units_margin = REMAINING_UNITS_ALERT_MARGIN * \
            record['package_size']
        previous_record = storage.get_previous_record()

        if record['days_left'] < REMAINING_DAYS_ALERT_MARGIN and (not previous_record or previous_record['days_left'] > REMAINING_DAYS_ALERT_MARGIN):
            warnings.append(
                f'WARNING: Only {record["days_left"]} days left. Remember to recharge your internet')
        if record['remaining_units'] < remaining_units_margin and (not previous_record or previous_record['remaining_units'] > remaining_units_margin):
            warnings.append(
                f'WARNING: Only {record["remaining_units"]} internet units left. Remember to recharge your internet')

        for warning in warnings:
            utility.logger.debug(warning)

        utility.logger.debug("Task completed successfully.")

        # notify user by opening log
        if warnings:
            os.startfile(
                r'F:\Programs\Python\Internet Consumption Monitor ICM\log.txt', 'open')
    except BaseException as error:
        utility.logger.debug(f"Task failed: {error}")
    finally:
        if scraper:
            scraper.browser.quit()


if __name__ == '__main__':
    run()
