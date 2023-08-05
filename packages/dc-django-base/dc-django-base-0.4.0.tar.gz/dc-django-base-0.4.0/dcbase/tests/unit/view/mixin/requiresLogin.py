from django.core.urlresolvers import reverse


class RequiresLogin(object):
    """
    Test mixin for views that require a user to be logged in.
    """

    def test_getRedirectsToLoginIfUserNotLoggedIn(self):
        self.logOut()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('account_login') + '?next={}'.format(self.url))

    def test_getReturnsStatusOkForLoggedInUsers(self):
        if not self.loggedInUser:
            self.createUser(logIn=True)
        response = self.client.get(self.url)
        self.assertResponseStatusIsOk(response)

