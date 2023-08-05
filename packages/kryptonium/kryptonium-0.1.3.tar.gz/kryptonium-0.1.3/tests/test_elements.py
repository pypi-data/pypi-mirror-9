from mock import Mock, patch, sentinel
from unittest import TestCase
from selenium.common.exceptions import NoSuchElementException

from krypton import elements
from krypton.pages import BasePage


class _BaseTestElement(TestCase):

    @patch('krypton.elements.WebElementSelect')
    def setUp(self, Select):
        self.browser = Mock()
        self.select = Select(return_value=Mock())
        self.configure()
        self.element = Mock()
        self.locator = 'div.element'

        class Element(elements.BaseElement):
            locator = self.locator

        class Elements(elements.List):
            locator = self.locator

        class SelectElement(elements.Select):
            locator = self.locator

        class Radio(elements.Radio):
            locator = self.locator

        class Page(BasePage):
            url = 'http://localhost'
            element = Element()
            elements = Elements()
            select = SelectElement()
            radio = Radio()

        self.page = Page(self.browser)

        try:
            self.execute()
        except NoSuchElementException as self.error:
            pass

    def configure(self):
        pass

    def test_find_by_css_selector(self):
        self.page.browser.find_element_by_css_selector\
            .assert_called_once_with(self.locator)


# Base.__get__

class DescribeGettingAnElementValue(_BaseTestElement):

    def execute(self):
        self.returned = self.page.element

    def test_return_an_element(self):
        self.assertEqual(
            self.returned,
            self.browser.find_element_by_css_selector.return_value,
        )


class DescribeGettingAnElementThatCannotBeFound(_BaseTestElement):

    def configure(self):
        self.browser.find_element_by_css_selector = Mock(
            side_effect=NoSuchElementException('original message ...'))

    def execute(self):
        self.returned = self.page.element

    def test_raise_a_NoSuchElementException(self):
        self.assertIsInstance(self.error, NoSuchElementException)

    def test_use_custom_message_in_exception(self):
        self.assertEqual(
            self.error.msg,
            'original message ... Element:div.element not found on Page.'
        )


# Base.__set__

class DescribeSettingTheValueOfAnElement(_BaseTestElement):

    def execute(self):
        self.page.element = 'some text'

    def test_enter_text_into_field(self):
        webelement = self.browser.find_element_by_css_selector.return_value
        webelement.send_keys.assert_called_once_with('some text')

    def test_be_cleared(self):
        webelement = self.browser.find_element_by_css_selector.return_value
        webelement.clear.assert_called_once_with()


# ReadOnly.__set__

class DescribeSettingTheValueofAReadOnlyElement(TestCase):

    def setUp(self):
        self.browser = Mock()
        self.locator = 'div.element'

        class ReadOnlyElement(elements.ReadOnly):
            locator = self.locator

        class Page(BasePage):
            url = 'http://localhost'
            element = ReadOnlyElement()

        self.page = Page(self.browser)

        try:
            self.page.element = 'something'
        except AttributeError as self.error:
            pass

    def test_raise_an_AttributeError(self):
        self.assertIsInstance(self.error, AttributeError)


# List.__get__

class DescribeGettingElements(_BaseTestElement):

    def execute(self):
        self.returned = self.page.elements

    def test_return_list_of_elements(self):
        self.assertEqual(
            self.returned,
            self.browser.find_elements_by_css_selector.return_value
        )

    def test_find_by_css_selector(self):
        self.page.browser.find_elements_by_css_selector\
            .assert_called_once_with(self.locator)


class DescribeGettingElementsThatCannotBeFound(_BaseTestElement):

    def configure(self):
        self.browser.find_elements_by_css_selector = Mock(
            side_effect=NoSuchElementException('original message ...'))

    def execute(self):
        self.returned = self.page.elements

    def test_raise_a_NoSuchElementException(self):
        self.assertIsInstance(self.error, NoSuchElementException)

    def test_use_custom_message_in_exception(self):
        self.assertEqual(
            self.error.msg,
            'original message ... Elements:div.element not found on Page.'
        )

    def test_find_by_css_selector(self):
        self.page.browser.find_elements_by_css_selector\
            .assert_called_once_with(self.locator)


# Select.__get__()

class DescribeGettingSelectElement(_BaseTestElement):

    def execute(self):
        self.returned = self.page.select

    def test_return_select(self):
        self.assertEqual(self.returned, self.select)


# Select.__set__()

class DescribeSettingValueSelectElement(_BaseTestElement):

    def execute(self):
        self.page.select = sentinel.option

    def test_select_option(self):
        self.select.select_by_visible_text\
            .assert_called_once_with(sentinel.option)


# Radio.__set__()

class DescribeSettingValueOfRadioButton(TestCase):

    @patch('krypton.elements.BaseElement.get_element')
    def setUp(self,  get):
        self.browser = Mock()
        self.element = Mock()
        self.element.get_attribute.return_value = sentinel.radio
        self.element_not_clicked = Mock()
        get.return_value = [self.element, self.element_not_clicked]
        self.locator = 'div.element'

        class Radio(elements.Radio):
            locator = self.locator

        class Page(BasePage):
            url = 'http://localhost'
            radio = Radio()

        self.page = Page(self.browser)
        self.page.radio = sentinel.radio

    def test_select_radio(self):
        self.element.click.assert_called_once_with()

    def test_not_click_if_value_not_match(self):
        self.assertFalse(self.element_not_clicked.click.called)
