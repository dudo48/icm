import os


TIMEZONE = "Africa/Cairo"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CSV_DELIMITER = ','
PACKAGE_LIFESPAN = 30  # days
TIMEOUT = 120  # max seconds to wait for page to load the required element
WAITING_TIME = 3 # seconds to wait before reading data present in an element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# alert if remaining units is less than this
REMAINING_UNITS_ALERT_MARGIN = 15

# alert if remaining days is less than this
REMAINING_DAYS_ALERT_MARGIN = 5

# if time until scraping is less than this limit then sleep the remaining duration
SLEEP_DURATION_LIMIT = 10 * 60  # seconds
MAX_SLEEP_DURATION = 60 * 60  # seconds

# run ICM every x days
RUN_INTERVAL_DAYS = 1
