from dcbase.tests.browser.pages.pageObject import PageObject


class ProfilePage(PageObject):
    _urlPattern = 'account_profile_user'
    _pageName = 'Profile'

    def clickProfileEdit(self):
        element = self.browser.find_element_by_id('edit-profile')
        element.click()

