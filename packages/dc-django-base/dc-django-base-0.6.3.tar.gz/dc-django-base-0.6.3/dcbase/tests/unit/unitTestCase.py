from dcbase.tests import BaseTestCase
from django.test import TestCase


class UnitTestCase(TestCase, BaseTestCase):
    """
    Base test case for unit tests using the Django test client.
    """
    def __init__(self, methodName):
        BaseTestCase.__init__(self)
        super().__init__(methodName)

    def tearDown(self):
        BaseTestCase.tearDown(self)
        super().tearDown()

    def logInAs(self, user, *, password=None):
        """
        Log in the given `User`. The user must have been created with one of the :method:`BaseTestCase.createUser`
        methods.

        :param user: The `User` to log in
        :param password: The password to use for log in. The password used to create the user will be used if none is given.
        """
        username = user.username
        password = self.getPasswordForUser(user, password)

        result = self.client.login(username=username, password=password)
        if not result:
            raise RuntimeError('Failed to login as user [{}] with password [{}]'.format(username, password))
        self._loggedInUser = user

    def logOut(self):
        """
        Shortcut method to log out the currently logged in user.
        """
        self.client.logout()

    def assertResponseStatusIsOk(self, response):
        self.assertEqual(200, response.status_code)

    def assertResponseStatusIsNotFound(self, response):
        self.assertEqual(404, response.status_code)

    def assertResponseStatusIsNotAuthorized(self, response):
        self.assertEqual(401, response.status_code)

