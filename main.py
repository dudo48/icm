import csv
import datetime
import time
import credentials
import sys
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

PACKAGE_SIZE = 140  # data units
MONTH = 30  # days
LOGIN_URL = "https://my.te.eg/#/home/signin"
USAGE_URL = "https://my.te.eg/#/offering/usage"
DAYS_LEFT_SELECTOR = "div.row:nth-child(4) > div:nth-child(2)"
PACKAGE_SIZE_SELECTOR = ".text-center > strong:nth-child(2)"
REMAINING_UNITS_SELECTOR = "span.text-dir:nth-child(4)"
DELIMITER = ','
TIMEOUT = 120  # time to wait for page to load the required element
REPORT_ROW_WIDTH = 40  # spaces to leave after each entry in report
MAXIMUM_TRIES = 5       # maximum amount to retry to get the record in case of failure
RETRY_INTERVAL = 10


def type_slowly(browser, element_id, text, delay):
    element = WebDriverWait(browser, TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    for char in text:
        element.send_keys(char)
        time.sleep(delay)


def create_record():
    # log in and get required data
    print("Opening browser...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    browser = webdriver.Chrome(options=options)

    browser.get(LOGIN_URL)

    try:
        print("Logging in...")
        type_slowly(browser, "MobileNumberID", credentials.USERNAME, 0.1)
        type_slowly(browser, "PasswordID", credentials.PASSWORD, 0.1)
        sign_in_element = WebDriverWait(browser, TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.ID, "singInBtn"))
        )
        sign_in_element.click()
        time.sleep(5)
        browser.get(USAGE_URL)

        print("Grabbing data...")
        days_left_element = WebDriverWait(browser, TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, DAYS_LEFT_SELECTOR))
        )
        package_size_element = WebDriverWait(browser, TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, PACKAGE_SIZE_SELECTOR))
        )
        remaining_units_element = WebDriverWait(browser, TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, REMAINING_UNITS_SELECTOR))
        )

        days_left = int(days_left_element.text.split(' ')[0])
        package_size = float(package_size_element.text.split(' ')[3])
        consumed_units = float(package_size_element.text.split(' ')[0])
        remaining_units = float(remaining_units_element.text.split(' ')[1])
        browser.quit()

    except Exception:
        # entered in case of failure of the program(like element not found)
        browser.quit()
        return []

    print("Creating new record...")

    # get table headers
    with open("databases/database.csv", mode='r') as database:
        csv_reader = csv.reader(database, delimiter=DELIMITER)
        table_headers = next(csv_reader)
        database.close()

    # access last day data
    with open("databases/last_day_data.csv", mode='r') as last_data:
        csv_reader = csv.reader(last_data, delimiter=DELIMITER)
        last_day_data = dict(zip(table_headers, next(csv_reader)))
        last_data.close()

    consumption_in_between = round(float(last_day_data["remaining units"]) - remaining_units, 2)

    last_date = datetime.datetime.strptime(last_day_data["date"], "%Y-%m-%d").date()   # string to datetime object
    today_date = datetime.date.today()
    # new monthly package started
    if days_left > int(last_day_data["days left"]) or abs(today_date - last_date).days >= MONTH:
        consumption_in_between = round(PACKAGE_SIZE - remaining_units, 2)

    consumed_percentage = round(float(consumed_units) / float(package_size), 3)
    projected_consumption = round(remaining_units / days_left, 2)
    average_consumption = round(consumed_units / (MONTH - days_left + 1), 2)

    new_row = []
    new_row.append(str(today_date))
    new_row.append(str(days_left))
    new_row.append(str(package_size))
    new_row.append(str(consumed_units))
    new_row.append(str(consumed_percentage))
    new_row.append(str(remaining_units))
    new_row.append(str(consumption_in_between))
    new_row.append(str(projected_consumption))
    new_row.append(str(average_consumption))

    return new_row


def add_to_csv_database(new_row):
    print("Adding record to CSV database...")
    with open("databases/database.csv", mode='a') as writer:
        writer.write('\n' + new_row)
        writer.close()


def add_to_sql_database(new_row):
    print("Adding record to SQL database...")
    conn = sqlite3.connect("databases/database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO InternetConsumption VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(new_row))
    conn.commit()
    conn.close()


def create_report(row):
    print("Creating report...")
    today_report = ""

    # get table headers
    with open("databases/database.csv", mode='r') as database:
        csv_reader = csv.reader(database, delimiter=DELIMITER)
        table_headers = next(csv_reader)
        database.close()

    for i in range(len(table_headers)):
        table_headers[i] = table_headers[i].title()  # capitalize each word of the string
        today_report += table_headers[i] + ":" + (" " * (REPORT_ROW_WIDTH - len(table_headers[i]))) + row[i]

        if i != len(table_headers) - 1:
            today_report += '\n'

    # write it to file
    with open("report.txt", mode='w') as writer:
        writer.write(today_report)
        writer.close()


# saves today data to separate file for quick access the next run of the program
def set_last_day_data(today_data):
    with open("databases/last_day_data.csv", mode='w') as writer:
        writer.write(today_data)
        writer.close()


def main():
    row = []
    for tries in range(MAXIMUM_TRIES):
        row = create_record()
        if row:     # if list isn't empty
            break
        if tries == MAXIMUM_TRIES - 1:
            sys.exit(1)     # used up all tries and failed
        print(f"Task failed: {MAXIMUM_TRIES - tries - 1} tries left.")
        print(f"Retrying in {RETRY_INTERVAL} seconds...")
        time.sleep(RETRY_INTERVAL)      # wait some time before retrying

    add_to_sql_database(row)
    row_string = DELIMITER.join(row)
    add_to_csv_database(row_string)
    set_last_day_data(row_string)
    create_report(row)

    print("Done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
