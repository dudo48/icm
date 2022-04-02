import datetime

MONTH = 30  # days
DELIMITER = ','
TIMEOUT = 120  # time to wait for page to load the required element
TABLE_HEADERS = ["Date", "Days Left", "Package Size", "Consumed Units", "Consumed Percentage", "Remaining Units",
                 "Consumption In-Between", "Projected Daily Consumption", "Average Consumption"]

# the scheduler runs the program between these times only(inclusive)
START_HOUR = datetime.time(22, 00)
END_HOUR = datetime.time(23, 59)

SCHEDULER_CHECK_INTERVAL = 5 * 60  # interval of seconds for the scheduler to check a possible run
