from dcbase.tests.unit import UnitTestCase
from dcbase.tests.unit.view.mixin import RequiresLogin
from django.core.urlresolvers import reverse


class TestEditUserView(UnitTestCase, RequiresLogin):
    url = reverse('account_profile_edit')

    def test_rendersUserEditTemplate(self):
        self.createUser(logIn=True)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'dcbase/profile_edit.html')

