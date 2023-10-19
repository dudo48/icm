import datetime

MONTH = 30  # days
DELIMITER = ','
TIMEOUT = 120  # time to wait for page to load the required element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# alert if remaining units / package size is less than this percentage
REMAINING_UNITS_ALERT_MARGIN = 0.10
REMAINING_DAYS_ALERT_MARGIN = 5     # alert if remaining days is less than x days
TYPE_SLOWLY_DELAY = 0.05

MIN_CHECK_INTERVAL = 15 * 60  # seconds
CHECK_INTERVAL_FACTOR = 0.1

PROJECT_ROOT = r"F:\Programs\Python\Internet Consumption Monitor ICM"
