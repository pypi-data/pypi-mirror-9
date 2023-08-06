"""Page class, intended to be sub classed as an abstraction for a real web page

Page classes collect the logic for how to use a certain part of the web site
under test into one area.

"""
from inspect import isclass
import time
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import TimeoutException, WebDriverWait

ELEMENT_TIMEOUT = 10


class SeleniumWrapper(object):

    TimeoutException = TimeoutException


    class ComponentMissing(Exception):
        pass

    def _get_component_class(self, component_or_selector):
        """Ensure we have a component class

        Either return argument if it's a component, get a registered component,
        or dynamically create a component.

        """
        if isclass(component_or_selector) and issubclass(
                component_or_selector, Component):
            return component_or_selector
        try:
            return self._registry[component_or_selector]
        except KeyError:
            return type(
                'DynamicComponent',
                (Component,), {
                    '_parent': self,
                    'selector': component_or_selector
                }
            )

    def get_component(self, component_or_selector):
        """Return an initialised component present in page

        takes either a component class to find in the page or a css selector.

        If the selector is not present in the page raises a ComponentMissing
        error.
        """
        ComponentClass = self._get_component_class(component_or_selector)

        try:
            return ComponentClass(self)
        except TimeoutException:
            raise self.ComponentMissing(
                '{} could not be found in page'.format(ComponentClass))

    def get_components(self, component_or_selector):
        """Return an list of initialised components present in page

        Returns an empty list if no components could be found
        """
        ComponentClass = self._get_component_class(component_or_selector)

        components = []
        try:
            elements = self.get_elements(ComponentClass.selector)
        except TimeoutException:
            return components

        for idx, element in enumerate(elements, 1):
            individualClass = self._get_component_class(
                    '{}:nth-child({})'.format(component_or_selector, idx))
            components.append(individualClass(self, element))

        return components

    def _wait_for_condition(self, condition, message='', driver=None):
        """Wait until the expected condition is true and return the result"""
        if not driver:
            driver = self._element
        return WebDriverWait(driver, ELEMENT_TIMEOUT).until(condition, message)

    def get_element(self, selector, driver=None):
        """Get the DOM element identified by the css selector"""
        return self._wait_for_condition(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector)),
            message='No element found with selector "{}".'.format(selector),
            driver=driver
        )

    def get_visible_element(self, selector):
        return self._wait_for_condition(
            ec.visibility_of_element_located((By.CSS_SELECTOR, selector)),
            message='No visible element found with selector "{}".'.format(
                selector)
        )

    def get_element_by_link_text(self, link_text):
        """Get the DOM element identified by the css selector"""
        return self._wait_for_condition(
            ec.presence_of_element_located((By.LINK_TEXT, link_text)),
            message='No link with text "{}".'.format(link_text)
        )

    def get_elements(self, selector):
        """Get a list of elements identified by the css selector"""
        return self._wait_for_condition(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )

    def get_attribute(self, attribute):
        return self._element.get_attribute(attribute)

    def wait_for_invisibility(self, selector):
        return self.assert_element_invisible(selector)

    def text_in_element(self, selector, text):
        return self._wait_for_condition(
            ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR, selector), text),
            message=u'"{}" not found in "{}".'.format(
                text, self.get_component(selector).text)
        )

    def has_text(self, text):
        self._update_element()
        if isinstance(self, Page):
            selector = 'body'
        else:
            selector = self.selector
        return self.text_in_element(selector, text)

    def assert_element_invisible(self, selector):
        return self._wait_for_condition(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, selector))
        )

    def _click(self, element, opens=None):
        """Click an element and return an appropriate component or page

        Element is a selenium WebElement, opens can be either a css
        selector or a subclass of Component
        """
        element.click()
        if opens:
            return self._get_component_class(opens)(self)

        if self.url != self.location() and self.location() in self._registry:
            return self._registry[self.location()](
                self.tc, driver=self._driver)
        return self

    def click(self, selector=None, opens=None):
        """Main method for interacting with a page or component

        Returns either self, a new page object based on browser url, or a
        page component based on the selector passed in as 'opens'.
        selector can be a css selector in the form of a string, or a
        selenium WebElement.

        """
        return self._click(self._ensure_element(selector), opens)

    def click_link(self, link_text, opens=None):
        return self._click(self.get_element_by_link_text(link_text), opens)

    def click_button(self, button_text, opens=None):
        """Find buttons on the page and click the first one with the text"""
        for button in self._element.find_elements_by_tag_name("button"):
            if button.text == button_text and button.is_displayed():
                return self._click(button, opens)
        raise AssertionError(
            "Could not find a button with the text '%s'" % (button_text,)
        )
    def _ensure_element(self, selector_or_element):
        if isinstance(selector_or_element, basestring):
            return self.get_element(selector_or_element)
        if isinstance(selector_or_element, Component):
            return self.get_element(selector_or_element.selector)
        if selector_or_element is None:
            # We hit this case when we want to click on the parent component
            return self._element
        return selector_or_element

    def location(self):
        return self._driver.current_url.split('?')[0]

    def select_option(self, selector, option_text):
        Select(self.get_element(selector)).select_by_visible_text(option_text)

    def clear(self, selector):
        try:
            self.get_visible_element(selector).clear()
        except (exceptions.InvalidElementStateException,
                exceptions.WebDriverException):
            raise exceptions.WebDriverException(
                'You cannot clear that element')

    def hover(self, selector, opens=None):
        ActionChains(self._driver).move_to_element(
            self.get_element(selector)).perform()
        if opens:
            return self._get_component_class(opens)(self)

    def enter_text(self, selector, text):
        """Enter text into DOM element identified by selector

        The function performs some error checking because as of Jan 2014
        send_keys on the element is unreliable at text entry.

        """
        element = self.get_visible_element(selector)
        for _ in range(5):
            element.send_keys(*text)
            try:
                value_in_place = element.get_attribute("value") or element.text
            except exceptions.StaleElementReferenceException:
                return
            expected = "".join([unicode(v) for v in text])
            if value_in_place == expected:
                return
            try:
                element.clear()
            except (exceptions.InvalidElementStateException,
                    exceptions.WebDriverException):
                return  # Element is not user editable and can't be cleared

            time.sleep(0.2)
        raise AssertionError("Unable to correctly type {}".format(text))


class RegisterMeta(type):

    def __init__(cls, name, bases, dct):
        if dct.get('url'):
            cls._registry[dct.get('url')] = cls
        elif dct.get('selector'):
            cls._registry[dct.get('selector')] = cls

        return super(RegisterMeta, cls).__init__(name, bases, dct)


class Registry(object):
    _registry = dict()


class BaseComponent(object):

    _element = None

    @property
    def text(self):
        try:
            return self._element.text
        except exceptions.StaleElementReferenceException:
            self._update_element()
            return self._element.text


    def _update_element(self):
        self._element = self.get_element(self.selector, driver=self._driver)


class Component(BaseComponent, SeleniumWrapper, Registry):
    __metaclass__ = RegisterMeta
    selector = None

    def __repr__(self):
        return '{}(selector="{}")'.format(
            self.__class__.__name__, self.selector)

    def __init__(self, parent, element=None):
        self.tc = parent.tc
        self._parent = parent
        self._driver = parent._driver
        if element:
            self._element = element
        else:
            self._update_element()

    @property
    def url(self):
        if isinstance(self._parent, Page):
            return self._parent.url
        return self._parent.url


class Page(BaseComponent, SeleniumWrapper, Registry):
    """Generic web page, intended to be subclassed

    Pages and Components are stored in a registry and switched to dynamically

    class LoginPage(Page):
        url = 'https://your-site.com/login

        def login(username, password):
            self.enter_text("input[name=username]", username)
            self.enter_text("input[name=password]", password)
            return self.click("input[type=submit]")
    """
    __metaclass__ = RegisterMeta
    url = None

    def __init__(self, tc, driver=None):
        self.selector = 'html'
        self.tc = tc
        if driver:
            self._driver = driver
        else:
            self._driver = tc._driver
        if self.location() != self.url:
            self._driver.get(self.url)
        self._update_element()
