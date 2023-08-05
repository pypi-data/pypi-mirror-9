import os
import json

from selenium import webdriver


def merge_dictionaries(dict_a, dict_b):
    return dict(dict_a.items() + dict_b.items())


def get_config():
    path = os.environ['KRYPTON_CONFIG']
    json_str = open(path).read()
    return json.loads(json_str)


def get_desired_capabilities():
    """Return an object that specifies the desired capabilities.

    Read environment variables that specify how the Selenium test
    should be run. Return a dictionary representation of those values.

    """
    config = get_config()
    browser = config['selenium']['browser']
    desired_capabilities = getattr(
        webdriver.DesiredCapabilities, browser)
    desired_capabilities = merge_dictionaries(
        desired_capabilities, config['selenium'])
    return desired_capabilities


def get_grid_config():
    """Return a URL where the selenium grid can be found."""
    config = get_config()['selenium']
    command_executor = "http://{url}:{port}/wd/hub".format(
        **config['hub'])
    return str(command_executor)


def get_application_settings():
    """Reads environment variables to retrieve application settings.

    This method will return an object of application settings retrieved from
    environment variables. A default value will be used if one is not found.

    """
    config = get_config()
    protocol = config['application']['protocol']
    if 'port' in config['application']:
        host = '{url}:{port}'.format(**config['application'])
    else:
        host = config['application']['url']
    return {'protocol': protocol, 'host': host}
