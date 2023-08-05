from unittest import TestCase
from mock import patch

from krypton.utils import *


class TestMergeDictionary(TestCase):
    @classmethod
    def setUp(cls):
        a = {'a': 1, 'b': 2}
        b = {'b': 3, 'c': 4}
        cls.returned = merge_dictionaries(a, b)

    def test_merged(self):
        self.assertEqual(self.returned, {'a': 1, 'b': 3, 'c': 4})


class TestGetConfig(TestCase):
    @classmethod
    @patch('krypton.utils.json')
    @patch('__builtin__.open')
    @patch('krypton.utils.os')
    def setUp(cls, os, mopen, json):
        cls.os = os
        cls.open = mopen
        cls.json = json
        cls.os.environ = {'KRYPTON_CONFIG': 'config'}
        cls.open().read.return_value = 'json_str'
        cls.json.loads.return_value = 'json'
        cls.returned = get_config()

    def test_open_path(self):
        self.open.assert_called_with('config')

    def test_json_load(self):
        self.json.loads.assert_called_once_with('json_str')

    def test_return(self):
        self.assertEqual(self.returned, 'json')


# get_desired_capabilities

class TestGettingDesiredCapabilities(TestCase):

    @patch('krypton.utils.get_config')
    def setUp(self, conf):
        self.get_config = conf
        self.get_config.return_value = {
            'selenium': {
                'browser': 'FIREFOX',
                'version': 'ANY',
                'platform': 'MAC',
            }
        }
        self.returned = get_desired_capabilities()

    def test_read_correct_config(self):
        self.get_config.assert_called_once_with()

    def test_return_desired_capabilities(self):
        desired_capabilities = {
            'browserName': 'firefox',
            'browser': 'FIREFOX',
            'javascriptEnabled': True,
            'platform': 'MAC',
            'version': 'ANY',
        }
        self.assertEqual(self.returned, desired_capabilities)


# get_grid_config

class TestGettingGridConfig(TestCase):

    @patch('krypton.utils.get_config')
    def setUp(self, conf):
        self.get_config = conf
        self.get_config.return_value = {
            "selenium": {
                "hub": {
                    "provider": "local",
                    "url": "localhost",
                    "port": "4444",
                }
            }
        }
        self.returned = get_grid_config()

    def test_return_selenium_url(self):
        self.assertEqual(self.returned, 'http://localhost:4444/wd/hub')


# get_application_settings

class TestGettingApplicationSettings(TestCase):

    @patch('krypton.utils.get_config')
    def setUp(self, conf):
        self.get_config = conf
        self.get_config.return_value = {
            'application': {
                'protocol': 'http',
                'url': 'example.com',
                'port': '80',
            }
        }
        self.returned = get_application_settings()

    def test_return_application_settings(self):
        settings = {
            'protocol': 'http',
            'host': 'example.com:80'
        }
        self.assertEqual(self.returned, settings)


class TestPortIsNotAvailable(TestCase):

    @patch('krypton.utils.get_config')
    def setUp(self, conf):
        self.get_config = conf
        self.get_config.return_value = {
            'application': {
                'protocol': 'http',
                'url': 'example.com',
            }
        }
        self.returned = get_application_settings()

    def test_return_desired_capabilities(self):
        settings = {
            'protocol': 'http',
            'host': 'example.com'
        }
        self.assertEqual(self.returned, settings)
