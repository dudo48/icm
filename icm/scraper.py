import contextlib
import dataclasses
import datetime
import os
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import select
from webdriver_manager.chrome import ChromeDriverManager

from icm import css_selector, url
from icm.config import config
from icm.database import Session
from icm.logger import logger
from icm.record import Record


def type_slowly(element: WebElement, text: str):
    for char in text:
        element.send_keys(char)
        time.sleep(0.05)


@contextlib.contextmanager
def login(headless: bool = True):
    """Context manager that yields an authenticated scraper."""
    options = Options()
    if headless:
        options.add_argument("headless")
        os.environ["WDM_LOG"] = "0"  # no logging console for webdriver

    logger.debug("Opening browser...")
    scraper = Scraper.from_options(options)
    logger.debug("Logging in...")
    scraper.login()
    try:
        yield scraper
    finally:
        scraper.browser.quit()


@dataclasses.dataclass
class Scraper:
    browser: WebDriver

    @classmethod
    def from_options(cls, options: Optional[Options] = None):
        if not options:
            options = Options()
        service = Service(ChromeDriverManager().install())
        return cls(webdriver.Chrome(service=service, options=options))

    @staticmethod
    def wait():
        return time.sleep(config["scraper"]["waiting_time"])

    def _get_renewal_date(self):
        self.browser.get(url.OVERVIEW)
        self.wait()

        renewal_date_element = self.browser.find_element(
            By.CSS_SELECTOR, css_selector.RENEWAL_DATE
        )
        renewal_date = datetime.datetime.strptime(renewal_date_element.text.split()[2][:-1], "%d-%m-%Y")
        return renewal_date

    def _get_consumed_units(self):
        self.browser.get(url.USAGE)
        self.wait()

        consumed_units_element = self.browser.find_element(
            By.CSS_SELECTOR, css_selector.CONSUMED_UNITS
        )
        consumed_units = float(consumed_units_element.text.split()[0])
        return consumed_units

    def _get_remaining_units(self):
        self.browser.get(url.USAGE)
        self.wait()

        remaining_units_element = self.browser.find_element(
            By.CSS_SELECTOR, css_selector.REMAINING_UNITS
        )
        remaining_units = float(remaining_units_element.text.split()[0])
        return remaining_units

    def login(self):
        self.browser.get(url.LOGIN)
        timeout: int = config["scraper"]["timeout"]

        # type service number
        service_number_element = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector.SERVICE_NUMBER)
            )
        )
        service_number_element.click()
        type_slowly(service_number_element, config["credentials"]["number"])

        # select service type
        service_type_element = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector.SERVICE_TYPE)
            )
        )
        service_type_element.click()
        internet_service_type_element = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector.INTERNET_SERVICE_TYPE)
            )
        )
        internet_service_type_element.click()

        # type password
        password_element = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector.PASSWORD)
            )
        )
        password_element.click()
        type_slowly(password_element, config["credentials"]["password"])

        # click log in button
        sign_in_element = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, css_selector.SIGN_IN_BUTTON)
            )
        )
        sign_in_element.click()
        WebDriverWait(self.browser, timeout).until(
            expected_conditions.url_to_be(url.INDEX)
        )

    def create_record(self):
        date = datetime.datetime.now()

        logger.debug("Retrieving consumed units...")
        consumed_units = self._get_consumed_units()

        logger.debug("Retrieving remaining units...")
        remaining_units = self._get_remaining_units()

        logger.debug("Retrieving renewal date...")
        renewal_date = self._get_renewal_date()

        consumption_since = consumed_units
        with Session() as session:
            latest_record = session.scalars(select(Record).order_by(Record.date.desc())).first()
            if latest_record and latest_record.renewal_date > date:
                consumption_since = consumed_units - latest_record.consumed_units

        return Record(
            date=date,
            renewal_date=renewal_date,
            remaining_units=remaining_units,
            consumed_units=consumed_units,
            consumption_since=consumption_since,
        )
