from django.core.urlresolvers import reverse
from django.views.generic import RedirectView


class ProfileView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('account_profile_user', kwargs={'username': self.request.user.username})

profileView = ProfileView.as_view()

