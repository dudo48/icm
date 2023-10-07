import datetime

MONTH = 30  # days
DELIMITER = ','
TIMEOUT = 120  # time to wait for page to load the required element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# the scheduler runs the program between these times only(inclusive)
START_HOUR = datetime.time(22, 00)
END_HOUR = datetime.time(23, 59)

# interval of seconds for the scheduler to check a possible run
SCHEDULER_CHECK_INTERVAL = 5 * 60
# alert if remaining units / package size is less than this percentage
REMAINING_UNITS_ALERT_MARGIN = 0.10
REMAINING_DAYS_ALERT_MARGIN = 5     # alert if remaining days is less than x days
TYPE_SLOWLY_DELAY = 0.05
