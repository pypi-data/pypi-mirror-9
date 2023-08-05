import os
from selenium import webdriver
from django.test import LiveServerTestCase

from dcbase.tests import BaseTestCase
from dcbase.tests.browser.pages.loginPage import LoginPage


class BrowserTestCase(LiveServerTestCase, BaseTestCase):
    _pageClass = None
    _browser = None
    _windowWidth = 1024
    _windowHeight = 768
    _requiresLogin = False
    _loggedInBrowserUser = None

    def __init__(self, methodName):
        BaseTestCase.__init__(self)
        super().__init__(methodName)
        self._urlFields = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        webDriverClassName = os.environ.get('BROWSER', 'Chrome')
        webDriverClass = getattr(webdriver, webDriverClassName)
        cls._browser = webDriverClass()
        cls._browser.set_window_size(cls._windowWidth, cls._windowHeight)

    @classmethod
    def tearDownClass(cls):
        cls._browser.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        if self._requiresLogin and not self._loggedInBrowserUser:
            user = self.createUser()
            self.logInAs(user)
            self._loggedInBrowserUser = user
        self.browseToPageUnderTest()

    @property
    def pageClass(self):
        return self._pageClass

    @property
    def browser(self):
        return self._browser

    def getWindowWidth(self):
        return self._windowWidth

    def setWindowWidth(self):
        self.browser.set_window_size(self.windowWidth, self.windowHeight)

    windowWidth = property(getWindowWidth, setWindowWidth)

    def getWindowHeight(self):
        return self._windowHeight

    def setWindowHeight(self):
        self.browser.set_window_size(self.windowWidth, self.windowHeight)

    windowHeight = property(getWindowHeight, setWindowHeight)

    def browseToPage(self, cls, **urlFields):
        self.page = cls.get(self._browser, self.live_server_url, **urlFields)

    def browseToPageUnderTest(self):
        self.browseToPage(self._pageClass, **self._urlFields)

    def logInAs(self, user, *, password=None):
        self.browseToPage(LoginPage)
        self.page.enterCredentials(user.username, self.getPasswordForUser(user, password))
        self.page = self.page.submit()

    def logOut(self):
        pass

