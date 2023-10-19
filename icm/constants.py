import datetime

PROJECT_ROOT = r"F:\Programs\Python\Internet Consumption Monitor ICM"
DELIMITER = ','
MONTH_DAYS = 30
HOUR_SECONDS = 3600
TYPE_SLOWLY_DELAY = 0.05
TIMEOUT = 120  # seconds to wait for page to load the required element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# alert if remaining units is less than this
REMAINING_UNITS_ALERT_MARGIN = 15

# alert if remaining days is less than this
REMAINING_DAYS_ALERT_MARGIN = 5
