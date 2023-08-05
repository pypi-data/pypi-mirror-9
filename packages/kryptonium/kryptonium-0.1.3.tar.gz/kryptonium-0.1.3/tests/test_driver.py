from mock import patch, sentinel
from unittest import TestCase

from krypton.driver import CustomDriver


class TestGettingCustomWebDriver(TestCase):
    @classmethod
    @patch('krypton.driver.get_grid_config')
    @patch('krypton.driver.get_desired_capabilities')
    @patch('krypton.driver.merge_dictionaries')
    @patch('krypton.driver.WebDriver.__init__')
    def setUp(cls, webdriver, merge, capabilities, grid):
        cls.grid = grid
        cls.grid.return_value = sentinel.url
        cls.capabilities = capabilities
        cls.capabilities.return_value = sentinel.capabilities
        cls.merge = merge
        cls.merge.return_value = sentinel.caps
        cls.webdriver = webdriver
        cls.driver = CustomDriver()

    def test_call_desired_capabilities(self):
        self.capabilities.assert_called_once_with()

    def test_merge_dictionary(self):
        self.merge.assert_called_once_with(sentinel.capabilities, {})

    def test_call_webdriver(self):
        self.webdriver.assert_called_once_with(
            desired_capabilities=sentinel.caps,
            command_executor=sentinel.url
        )

    def test_call_get_grid_config(self):
        self.grid.assert_called_once_with()
