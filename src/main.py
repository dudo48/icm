import sys
import time
from src import constants, storage
from src.scraper import Scraper


def run():
    record = []
    for tries in range(constants.MAXIMUM_TRIES):
        print("Opening browser...")
        scraper = Scraper()
        try:
            print("Logging In...")
            scraper.login()
            time.sleep(5)
            print("Grabbing Data...")
            record = scraper.create_record()
            scraper.browser.quit()
            break
        except:
            scraper.browser.quit()
            print(f"Task failed: {constants.MAXIMUM_TRIES - tries - 1} tries left.")
            if tries == constants.MAXIMUM_TRIES - 1:
                return 1  # used up all tries and failed
            print(f"Retrying in {constants.RETRY_INTERVAL} seconds...")
            time.sleep(constants.RETRY_INTERVAL)  # wait some time before retrying

    print("Adding Data To Databases...")
    storage.add_to_sql_database(record)
    storage.add_to_csv_database(record)
    storage.set_previous_record(record)
    storage.create_report(record)
    print("Done!")
    time.sleep(5)
    return 0


if __name__ == '__main__':
    sys.exit(run())
