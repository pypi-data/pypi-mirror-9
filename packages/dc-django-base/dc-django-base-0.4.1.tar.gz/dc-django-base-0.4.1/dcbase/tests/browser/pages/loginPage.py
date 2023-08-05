from dcbase.tests.browser.pages.pageObject import PageObject


class LoginPage(PageObject):
    _urlPattern = 'account_login'
    _pageName = 'Login'

    def enterCredentials(self, username, password):
        self.enterUserName(username)
        self.enterPassword(password)

    def enterUserName(self, username):
        element = self.browser.find_element_by_id('id_login')
        element.clear()
        element.send_keys(username)

    def enterPassword(self, password):
        element = self.browser.find_element_by_id('id_password')
        element.clear()
        element.send_keys(password)

    def submit(self):
        element = self.browser.find_element_by_id('sign-in-btn')
        element.click()
