from dcbase.models import UserProfile
from dcbase.tests.unit import UnitTestCase
from django.utils import translation
from django.utils.translation import LANGUAGE_SESSION_KEY


class TestUserProfile(UnitTestCase):
    def test_profileIsAddedWhenUserIsCreated(self):
        user = self.createUser()
        self.assertIsInstance(user.profile, UserProfile)

    def test_profileIsCreatedWithCurrentLanguage(self):
        language = 'fr'
        translation.activate(language)
        user = self.createUser()
        self.assertEqual(language, user.profile.language)

    def test_loggingInSetsLanguageFromProfile(self):
        initialLanguage = 'en'
        translation.activate(initialLanguage)

        user = self.createUser()
        user.profile.language = 'fr'
        user.profile.save()
        self.logOut()

        self.assertEqual(initialLanguage, translation.get_language())

        self.logInAs(user)
        self.assertEqual('fr', self.client.session[LANGUAGE_SESSION_KEY])

