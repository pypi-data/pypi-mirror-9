from mock import Mock, patch, sentinel
from unittest import TestCase

from krypton.connection import (
    Browser,
    CONFIG
)


class _BaseExecuteScript(TestCase):

    @patch('krypton.connection.Browser.__init__', return_value=None)
    def setUp(self, _):
        self.browser = Browser()
        self.browser.execute_script = Mock()
        self.execute()

    def test_execute_script(self):
        self.assertEqual(self.browser.execute_script.call_count, 1)


# Browser._record_ajax_post

class TestRecordingAnAJAXPost(_BaseExecuteScript):

    def execute(self):
        self.browser._record_ajax_post()


# Browser._record_ajax_complete

class TestRecordingAJAXComplete(_BaseExecuteScript):

    def execute(self):
        self.browser._record_ajax_complete()


# Browser.navigate

class TestNavigatingToAURL(TestCase):

    @patch('krypton.connection.Browser.__init__', return_value=None)
    @patch('krypton.connection.get_application_settings')
    @patch('krypton.connection.sleep')
    def setUp(self, sleep, get_application_settings, _):
        self.sleep = sleep
        application_settings = {
            'protocol': 'https',
            'host': 'example.com'
        }
        self.get_application_settings = get_application_settings
        self.get_application_settings.return_value = application_settings
        self.browser = Browser()
        self.browser.get = Mock()
        self.browser.go_to_url = Mock()
        self.browser.navigate('page')

    def test_sleep_for_data_indexing_time(self):
        self.sleep.assert_called_once_with(
            CONFIG['backend_data_indexing_time'])

    def test_go_to_url(self):
        self.browser.go_to_url.assert_called_once_with(
            'https://example.com/page')


# Drive.go_to_url

class TestGoToAnURL(TestCase):

    @patch('krypton.connection.Browser.__init__', return_value=None)
    @patch.object(Browser, 'current_url')
    def setUp(self, current_url, _):
        self.driver = Browser()
        self.driver.current_url = current_url
        self.driver.get = Mock()
        self.driver.maximize_window = Mock()
        self.driver._record_ajax_post = Mock()
        self.driver._record_ajax_complete = Mock()
        self.driver.go_to_url(sentinel.url)

    def test_get_page_with_url(self):
        self.driver.get.assert_called_once_with(sentinel.url)

    def test_maximize_the_window(self):
        self.driver.maximize_window.assert_called_once_with()

    def test_record_ajax_posts(self):
        self.driver._record_ajax_post.assert_called_once_with()

    def test_record_ajax_complete(self):
        self.driver._record_ajax_complete.assert_called_once_with()


class TestNavigatingToCurrentURL(TestCase):

    @patch('krypton.connection.Browser.__init__', return_value=None)
    @patch.object(Browser, 'current_url')
    @patch('krypton.connection.get_application_settings')
    @patch('krypton.connection.sleep')
    @patch('krypton.connection.urljoin', return_value=sentinel.url)
    def setUp(self, join, sleep, get_application_settings, current_url, _):
        self.sleep = sleep
        application_settings = {
            'protocol': sentinel.protocol,
            'host': sentinel.host,
            'port': sentinel.port,
        }
        self.get_application_settings = get_application_settings
        self.get_application_settings.return_value = application_settings
        self.join = Mock()
        self.driver = Browser()
        self.driver.current_url = sentinel.url
        self.driver.get = Mock()
        self.driver.maximize_window = Mock()
        self.driver._record_ajax_post = Mock()
        self.driver._record_ajax_complete = Mock()
        self.driver.navigate(sentinel.page)

    def test_not_navigate_to_same_url(self):
        self.assertFalse(self.driver.get.called)
