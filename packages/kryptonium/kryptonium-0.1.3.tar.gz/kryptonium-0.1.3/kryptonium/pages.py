from datetime import timedelta
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from connection import CONFIG


class BasePage(object):
    """A base page object.

    A Page is a representation of a browser controlled web page. A page is
    typically comprised of Elements and functions that operate on that page.

    """
    def __init__(self, browser):
        self.browser = browser
        self.browser.navigate(self.url)

    def wait_for(self, func, *args, **kwargs):
        """Wait until a `func` returns without raising an AssertionError."""
        MAX_WAIT = CONFIG['page_load_time']
        SLEEP_INTERVAL = CONFIG['sleep_interval']

        max_wait = timedelta(0, MAX_WAIT, 0)
        elapsed_time = max_wait
        interval = timedelta(0, SLEEP_INTERVAL, 0)
        while elapsed_time:
            try:
                func(*args, **kwargs)
                return
            except AssertionError:
                sleep(SLEEP_INTERVAL)
                elapsed_time = elapsed_time - interval
        raise AssertionError

    def explicit_wait(self, locator, seconds=10):
        """Explicitly wait for an element to show up"""
        WebDriverWait(self.browser, seconds).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, locator)))
