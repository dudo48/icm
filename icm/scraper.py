import datetime
import json
import time
from subprocess import CREATE_NO_WINDOW

import credentials
import css_selectors
import storage
import urls
from constants import PACKAGE_LIFESPAN, TIMEOUT
from logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:
    def __init__(self, debug_mode=False):

        # initialize browser
        options = Options()
        service = Service(ChromeDriverManager().install())
        if not debug_mode:
            options.add_argument("headless")
            options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])

        self.browser = webdriver.Chrome(options=options, service=service)

    # selenium send keys but with a delay
    def type_slowly(self, element, text):
        for c in text:
            element.send_keys(c)
            time.sleep(0.1)

    def login(self):
        self.browser.get(urls.LOGIN)

        # type user name/number
        service_number_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.SERVICE_NUMBER))
        )
        service_number_element.click()
        self.type_slowly(service_number_element, credentials.USERNAME)

        # select service type
        service_type_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.SERVICE_TYPE))
        )
        service_type_element.click()
        internet_service_type_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.INTERNET_SERVICE_TYPE))
        )
        internet_service_type_element.click()

        # type password
        password_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.PASSWORD))
        )
        password_element.click()
        self.type_slowly(password_element, credentials.PASSWORD)

        # click log in button
        sign_in_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.SIGN_IN_BUTTON))
        )
        sign_in_element.click()
        WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.url_to_be(urls.INDEX)
        )

    def get_days_left(self):
        logger.debug('Retrieving days left...')
        self.browser.get(urls.OVERVIEW)

        days_left_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.DAYS_LEFT))
        )

        days_left = int(days_left_element.text.split()[3])
        return days_left

    def get_consumed_units(self):
        logger.debug('Retrieving consumed units...')
        self.browser.get(urls.USAGE)

        consumed_units_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.CONSUMED_UNITS))
        )

        consumed_units = float(consumed_units_element.text.split()[0])
        return consumed_units

    def get_remaining_units(self):
        logger.debug('Retrieving remaining units...')
        self.browser.get(urls.USAGE)

        remaining_units_element = WebDriverWait(self.browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selectors.REMAINING_UNITS))
        )
        remaining_units = float(remaining_units_element.text.split()[0])
        return remaining_units

    def create_record(self, previous_record):
        date = datetime.date.today()
        days_left = self.get_days_left()
        remaining_units = self.get_remaining_units()
        consumed_units = self.get_consumed_units()
        package_size = remaining_units + consumed_units
        consumed_percentage = round(
            float(consumed_units) / float(package_size), 3)
        projected_consumption = round(remaining_units / days_left, 2)
        average_consumption = round(
            consumed_units / (PACKAGE_LIFESPAN - days_left + 1), 2)

        # calculate consumption in between using previous record data
        if previous_record:
            consumption_in_between = round(
                consumed_units - previous_record['consumed_units'], 2)

            # check if new month started
            previous_date = datetime.datetime.strptime(
                previous_record['date'], '%Y-%m-%d').date()
            previous_days_left = previous_record['days_left']
            if days_left > previous_days_left or abs(date - previous_date).days >= PACKAGE_LIFESPAN:
                consumption_in_between = round(
                    package_size - remaining_units, 2)
        else:
            consumption_in_between = consumed_units

        record = {
            'date': str(date),
            'days_left': days_left,
            'package_size': package_size,
            'consumed_units': consumed_units,
            'consumed_percentage': consumed_percentage,
            'remaining_units': remaining_units,
            'consumption_in_between': consumption_in_between,
            'projected_consumption': projected_consumption,
            'average_consumption': average_consumption
        }

        return record
