import time
import constants
import storage
import utility
import ctypes
from scraper import Scraper


def run():
    utility.logger.debug("Running ICM...")
    scraper = None
    try:
        utility.logger.debug("Opening browser...")
        scraper = Scraper()

        utility.logger.debug("Logging in...")
        scraper.login()
        time.sleep(5)

        utility.logger.debug("Grabbing data...")
        record = scraper.create_record()

        utility.logger.debug("Adding data to databases...")
        storage.add_to_sql_database(record)
        storage.add_to_csv_database(record)
        storage.create_report(record)
        storage.set_previous_record(record)

        # warning message boxes
        remaining_units_margin = constants.REMAINING_UNITS_ALERT_MARGIN * record['package_size']
        previous_remaining_units = record['remaining_units'] + record['consumption_in_between']
        if record['days_left'] < constants.REMAINING_DAYS_ALERT_MARGIN:
            ctypes.windll.user32.MessageBoxW(0, f'Only {record["days_left"]} days left. Remember to '
                                                f'recharge your internet', 'ICM: Internet Consumption Manager', 48)
        elif record['remaining_units'] < remaining_units_margin < previous_remaining_units:
            ctypes.windll.user32.MessageBoxW(0, f'Only {record["remaining_units"]} internet units left. Remember to '
                                                f'recharge your internet', 'ICM: Internet Consumption Manager', 48)

        utility.logger.debug("Task completed successfully.")
    except BaseException as error:
        utility.logger.debug(f"Task failed: {error}")
    finally:
        if scraper:
            scraper.browser.quit()


if __name__ == '__main__':
    run()
