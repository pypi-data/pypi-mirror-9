class BaseComponent(object):
    """A base component object.

    A base component is a collection of elements in a page.

    """
    def __init__(self, browser):
        self.browser = browser
