import string

from abc import ABC, abstractmethod
from allauth.account.models import EmailAddress
from random import choice
from django.contrib.auth.models import User
from django.utils import translation


class BaseTestCase(ABC):
    def __init__(self):
        self._loggedInUser = None
        self._passwordsByUser = {}

    def tearDown(self):
        translation.activate('en')

    @abstractmethod
    def logInAs(self, user, *, password=None):
        pass

    @abstractmethod
    def logOut(self):
        pass

    @property
    def loggedInUser(self):
        return self._loggedInUser

    def randStr(self, length=10):
        """
        Create a random string of ascii letters and digits

        :param length: length of the string. default = 10 characters
        :return: a randomized string
        """
        return ''.join(choice(string.ascii_letters + string.digits) for x in range(length))

    def createUser(self, userName=None, password=None, *, email=None, logIn=False):
        """
        Create a `User` in the database. Log the user in using the :method:`UnitTestCase.logInAs` or
        :method:`BrowserTestCase.logInAs` method.

        :param userName: Name for the user. A random username will be created if none is given.
        :param password: Password for the user. A random password will be created if none is given.
        :param email: Email address for the user. A random email address will be created if none is given.
        :param logIn: True if this user should be logged in after creation. Default is False.
        :return: The newly created `User` object.
        """
        userName = userName or self.randStr()
        password = password or self.randStr()
        email = email or '%s@host.com' % self.randStr()

        user = User.objects.create_user(username=userName, password=password, email=email, first_name=self.randStr(), last_name=self.randStr())
        self._cachePasswordForUser(user, password)

        EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)

        if logIn:
            self.logInAs(user)

        return user

    def createAdminUser(self, userName=None, password=None, *, email=None, save=True, logIn=False):
        """
        As :method:`createUser` except that the new user has the is_staff flag.
        """
        user = self.createUser(userName, password, email=email, logIn=logIn)
        user.is_staff = True
        if save:
            user.save()
        return user

    def createSuperUser(self, userName=None, password=None, email=None, logIn=False):
        """
        As :method:`createUser` except that the new user has the is_staff and is_superuser flags.
        """
        user = self.createAdminUser(userName, password, email=email, save=False, logIn=logIn)
        user.is_superuser = True
        user.save()
        return user

    def expireSession(self, session):
        """
        Cause the given session to expire immediately.

        :param session: The session to expire.
        """
        session.set_expiry(-1)
        session.save()

    def getPasswordForUser(self, user, default=None):
        """
        Return the cached password for the given user.

        :param user: The user for whom the password should be retreived
        :param default: A default password to return if no cached password is found
        """
        return self._passwordsByUser.get(user, default)

    def _cachePasswordForUser(self, user, password):
        self._passwordsByUser[user] = password

