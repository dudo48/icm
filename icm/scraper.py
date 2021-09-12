import datetime
import pickle
import time
import constants
import utility
import css_selectors
import urls
import credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW


class Scraper:
    def __init__(self, debug_mode=False):

        # initialize browser
        options = Options()
        service = Service("path/to/chromedriver")
        if not debug_mode:
            options.headless = True
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            service.creationflags = CREATE_NO_WINDOW

        self.browser = webdriver.Chrome(options=options, service=service)

    def login(self):

        self.browser.get(urls.LOGIN)

        # type user name/number
        service_number_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.SERVICE_NUMBER))
        )
        service_number_element.click()
        utility.type_slowly(service_number_element, credentials.USERNAME)

        # type password
        password_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.PASSWORD))
        )
        password_element.click()
        utility.type_slowly(password_element, credentials.PASSWORD)

        # click log in button
        sign_in_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.SIGN_IN_BUTTON))
        )
        sign_in_element.click()

    def get_days_left(self):
        self.browser.get(urls.OVERVIEW)

        days_left_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.DAYS_LEFT))
        )
        time.sleep(1)

        days_left = int(days_left_element.text.split()[3])
        return days_left

    def get_consumed_units(self):
        self.browser.get(urls.USAGE)

        consumed_units_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.CONSUMED_UNITS))
        )
        time.sleep(1)

        consumed_units = float(consumed_units_element.text.split()[0])
        return consumed_units

    def get_remaining_units(self):
        self.browser.get(urls.USAGE)

        remaining_units_element = WebDriverWait(self.browser, constants.TIMEOUT).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selectors.REMAINING_UNITS))
        )
        time.sleep(1)

        remaining_units = float(remaining_units_element.text.split()[0])
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

        # calculate consumption in between using previous record data
        with open("../persistent/previous_record", 'rb') as file:
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
