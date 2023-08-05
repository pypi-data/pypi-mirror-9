from mock import Mock, patch, sentinel
from unittest import TestCase

from krypton.pages import BasePage
from krypton.connection import CONFIG


class Page(BasePage):
    url = 'example'


# Base

class TestBasePage(TestCase):

    @patch('krypton.connection.Browser.__new__')
    def setUp(self, _):
        self.browser = Mock()
        self.page = Page(self.browser)

    def test_navigate_to_url(self):
        self.browser.navigate.assert_called_once_with(self.page.url)


# Base.wait_for

class _BaseWaiting(TestCase):

    @patch('krypton.connection.Browser.__new__')
    @patch('krypton.pages.sleep')
    def setUp(self, sleep, _):
        self.sleep = sleep
        self.browser = Mock()
        self.page = Page(self.browser)
        self.configure()
        try:
            self.page.wait_for(self.function)
        except AssertionError as self.error:
            pass

    def configure(self):
        self.function = Mock(side_effect=[AssertionError, True])

    def test_call_function(self):
        self.function.assert_called_once()


class TestWaiting(_BaseWaiting):

    def test_call_sleep(self):
        self.sleep.assert_called_once_with(CONFIG['sleep_interval'])


class TestWaitingAndTimesOut(_BaseWaiting):

    def configure(self):
        self.function = Mock(side_effect=AssertionError)

    def test_call_sleep(self):
        self.sleep.assert_called_with(CONFIG['sleep_interval'])
        self.assertEqual(CONFIG['page_load_time'], self.sleep.call_count)

    def test_raise_AssertionError(self):
        self.assertIsInstance(self.error, AssertionError)
