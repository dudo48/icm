import datetime

TIMEZONE = "Africa/Cairo"
PROJECT_ROOT = r"F:\Programs\Python\Internet Consumption Monitor ICM"
CSV_DELIMITER = ','
PACKAGE_LIFESPAN = 30  # days
TIMEOUT = 120  # seconds to wait for page to load the required element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# alert if remaining units is less than this
REMAINING_UNITS_ALERT_MARGIN = 15

# alert if remaining days is less than this
REMAINING_DAYS_ALERT_MARGIN = 5

# if time until scraping is less than this limit then sleep the remaining duration
SLEEP_DURATION_LIMIT = 10 * 60  # seconds
MAX_SLEEP_DURATION = 3 * 60 * 60  # seconds
