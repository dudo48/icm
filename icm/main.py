import sys
import time
import constants
import storage
import utility
from scraper import Scraper


def run():
    record = []
    for tries in range(constants.MAXIMUM_TRIES):
        utility.logger.debug("Opening browser...")
        scraper = Scraper()
        try:
            utility.logger.debug("Logging in...")
            scraper.login()
            time.sleep(5)
            utility.logger.debug("Grabbing data...")
            record = scraper.create_record()
            scraper.browser.quit()
            break
        except:
            scraper.browser.quit()
            utility.logger.debug(f"Task failed: {constants.MAXIMUM_TRIES - tries - 1} tries left.")
            if tries == constants.MAXIMUM_TRIES - 1:
                return 1  # used up all tries and failed
            utility.logger.debug(f"Retrying in {constants.RETRY_INTERVAL} seconds...")
            time.sleep(constants.RETRY_INTERVAL)  # wait some time before retrying

    utility.logger.debug("Adding data to databases...")
    storage.add_to_sql_database(record)
    storage.add_to_csv_database(record)
    storage.set_previous_record(record)
    storage.create_report(record)
    utility.logger.debug("Done!")
    time.sleep(5)
    return 0


if __name__ == '__main__':
    sys.exit(run())
