import time
import constants
import storage
import utility
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
        storage.set_previous_record(record)
        storage.create_report(record)
        utility.logger.debug("Task completed successfully.")
    except BaseException as error:
        utility.logger.debug(f"Task failed: {error}")
    finally:
        if scraper:
            scraper.browser.quit()


if __name__ == '__main__':
    run()
