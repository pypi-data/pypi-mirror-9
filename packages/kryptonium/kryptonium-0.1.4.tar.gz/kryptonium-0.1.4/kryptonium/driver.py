from utils import (
    get_desired_capabilities,
    get_grid_config,
    merge_dictionaries
)
from selenium.webdriver.remote.webdriver import WebDriver


class CustomDriver(WebDriver):
    def __init__(self, capabilities=None):
        capabilities = capabilities or {}
        caps = merge_dictionaries(
            get_desired_capabilities(), capabilities)
        super(CustomDriver, self).__init__(
            desired_capabilities=caps,
            command_executor=get_grid_config()
        )
