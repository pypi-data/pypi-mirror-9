from dcbase.tests.browser import BrowserTestCase
from dcbase.tests.browser.pages.profileEditPage import ProfileEditPage
from dcbase.tests.browser.pages.profilePage import ProfilePage


class TestProfilePage(BrowserTestCase):
    _pageClass = ProfilePage

    def setUp(self):
        user = self.createUser()
        self.logInAs(user)
        self._urlFields['username'] = user.username
        super().setUp()

    def test_editProfileButtonGoesToProfileEditPage(self):
        self.page.clickProfileEdit()
        ProfileEditPage(self.browser)

