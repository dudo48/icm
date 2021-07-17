import datetime
import pickle

import constants
import selectors

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import credentials
import urls
import utility


class Scraper:
    def __init__(self, debug_mode=False):

        # initialize browser
        options = Options()
        if not debug_mode:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument("--log-level=3")

        self.browser = webdriver.Chrome(options=options)

    def login(self):

        self.browser.get(urls.LOGIN)
        # type user name/number
        service_number_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.SERVICE_NUMBER))
        )
        utility.type_slowly(service_number_element, credentials.USERNAME)

        # type password
        password_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.PASSWORD))
        )
        utility.type_slowly(password_element, credentials.PASSWORD)

        # click log in button
        sign_in_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.SIGN_IN_BUTTON))
        )
        sign_in_element.click()

    def get_days_left(self):
        self.browser.get(urls.OVERVIEW)

        days_left_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.DAYS_LEFT))
        )

        days_left = int(days_left_element.text.split(' ')[3])
        return days_left

    def get_consumed_units(self):
        self.browser.get(urls.USAGE)

        consumed_units_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.CONSUMED_UNITS))
        )

        consumed_units = float(consumed_units_element.text.split(' ')[0])
        return consumed_units

    def get_remaining_units(self):
        self.browser.get(urls.USAGE)

        remaining_units_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selectors.REMAINING_UNITS))
        )

        remaining_units = float(remaining_units_element.text.split(' ')[0])
        return remaining_units

    def create_record(self):
        today_date = datetime.date.today()
        days_left = self.get_days_left()
        remaining_units = self.get_remaining_units()
        consumed_units = self.get_consumed_units()
        package_size = remaining_units + consumed_units
        consumed_percentage = round(float(consumed_units) / float(package_size), 3)
        projected_consumption = round(remaining_units / days_left, 2)
        average_consumption = round(consumed_units / (constants.MONTH - days_left + 1), 2)

        with open("previous_record", 'rb') as file:
            previous_record = pickle.load(file)
            previous_consumed_units = previous_record[3]
            consumption_in_between = round(consumed_units - previous_consumed_units, 2)

            # new monthly package started
            previous_date = previous_record[0]
            previous_days_left = previous_record[1]
            if days_left > previous_days_left or abs(today_date - previous_date).days >= constants.MONTH:
                consumption_in_between = round(package_size - remaining_units, 2)


        record = []
        record.append(today_date)
        record.append(days_left)
        record.append(package_size)
        record.append(consumed_units)
        record.append(consumed_percentage)
        record.append(remaining_units)
        record.append(consumption_in_between)
        record.append(projected_consumption)
        record.append(average_consumption)

        return record
