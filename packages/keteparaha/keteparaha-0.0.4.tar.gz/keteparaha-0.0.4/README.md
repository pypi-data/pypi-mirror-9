Keteparaha
==========

Keteparaha is a collection of tools to help when functional testing

It contains utilities that assist with tasks like running a browser in a
headless environment, or checking that emails have been sent, or a file has
been uploaded to a server, or common testing flow control like retrying or
ignoring certain errors.

:copyright: (c) 2015 by Hansel Dunlop.

:license: GPLv3, see LICENSE for more details


BrowserTestCase
---------------

A browser test case for testing web applications. Subclass it and call the
`start_browser` method with the name of the browser you want to test with.
Closing the browser is handled automatically. For example:

    from test_helpers import BrowserTestCase


    class YourTestCase(BrowserTestCase):

        def setUp(self):
            self.browser = self.start_browser("Firefox")

        def test_page_loads(self):
            self.browser.get('127.0.0.1:8080')

            self.assertIn("Hello, World", self.body_text)


HeadlessBrowserTestCase
-----------------------

Requires XvFB to be installed (`sudo apt-get install xvfb`).

Designed for testing web applications on a headless server, probably running
as part of continuous integration. Usage is exactly like the BrowserTestCase
except that you won't see a browser window open, everything should be done
inside a virtual display.

The example below would run Firefox inside a virtual display with a width of
1200px and height of 900px.

    from test_helpers import HeadlessBrowserTestCase


    class YourTestCase(HeadlessBrowserTestCase):

        def setUp(self):
            self.browser = self.start_browser("Firefox", size=(1200, 900))

Remaining keyword arguments to start browser will be passed down to the
virtual display driver. But the other defaults are generally sensible.

Page
----

The Page class represents a page in your application and should be subclassed
and extended. It's really just a suggestion of how you might organise your
tests.

    from test_helpers import Page


    class YourDashboard(Page):

        def login(self, username, password):
            self.click_button_with_text("Login")
            self.get_via_css("input[name=username]").send_keys(username)
            self.get_via_css("input[name=password]").send_keys(password)
            self.get_via_css("input[type=submit]").click()

        def assert_logged_in(self):
            self.get_via_css(".account-details").is_displayed()


    class YourTestCase(BrowserTestCase):

        def test_login_works(self):
            dashboard = YourDashboard(browser=self.start_browser())
            dashboard.login()

            dashboard.assert_logged_in()

Email
-----

The email module contains a imap client written to interact with gmail. This
is especially useful if your organiation uses Google Apps and you're running
tests against it.


Flow Control
------------

This module contains three functions that are intended to make flow control in
testing situations less painful. They can be used as decorators. They are:

* retry
* ignore
* fallback
