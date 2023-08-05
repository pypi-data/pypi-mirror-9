from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select as WebElementSelect


class BaseElement(object):
    method = 'find_element_by_css_selector'

    def __get__(self, obj, cls=None):
        try:
            element = self.get_element(obj)
            return element

        except NoSuchElementException as error:
            error.msg = '{0} {1}:{2} not found on {3}.'\
                .format(
                    error.msg,
                    self.__class__.__name__,
                    self.locator,
                    cls.__name__)
            raise error

    def __set__(self, obj, value):
        element = self.get_element(obj)
        element.clear()
        element.send_keys(value)

    @classmethod
    def get_element(cls, obj):
        return getattr(obj.browser, cls.method)(cls.locator)


class ReadOnly(BaseElement):
    def __set__(self, obj, value):
        raise AttributeError


class List(BaseElement):
    method = 'find_elements_by_css_selector'


class Select(BaseElement):
    def __get__(self, obj, cls=None):
        element = super(Select, self).__get__(obj, cls)
        return WebElementSelect(element)

    def __set__(self, obj, value):
        element = self.get_element(obj)
        select = WebElementSelect(element)
        select.select_by_visible_text(value)


class Radio(List):
    def __set__(self, obj, value):
        for element in self.get_element(obj):
            if element.get_attribute('value') == value:
                element.click()
