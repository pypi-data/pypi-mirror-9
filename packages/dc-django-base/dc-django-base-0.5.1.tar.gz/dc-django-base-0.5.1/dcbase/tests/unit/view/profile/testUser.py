from dcbase.tests.unit import UnitTestCase
from django.core.urlresolvers import reverse


class TestUserView(UnitTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.createUser()
        self.url = self._createUrl(self.user.username)
        self.response = self.client.get(self.url)

    def _createUrl(self, username):
        return reverse('account_profile_user', kwargs={'username': username})

    def test_rendersProfileTemplate(self):
        self.assertTemplateUsed(self.response, 'dcbase/profile.html')

    def test_contextContainsUserAsGivenInUrl(self):
        self.assertEqual(self.user, self.response.context['profileUser'])

    def test_returnsNotFoundStatusIfUserNameIsInvalid(self):
        url = self._createUrl(self.randStr())
        response = self.client.get(url)
        self.assertResponseStatusIsNotFound(response)

