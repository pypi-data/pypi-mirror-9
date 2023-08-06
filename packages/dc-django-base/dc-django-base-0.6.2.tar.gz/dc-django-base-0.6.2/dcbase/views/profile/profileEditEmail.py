from allauth.account.views import EmailView
from dcbase.lib.profileEditor import ProfileEditor
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _


class ProfileEditEmailView(EmailView):
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ProfileEditor.add_profile_edit_context(kwargs, _('E-mail'), _('E-mail Addresses'))
        return kwargs

profileEditEmailView = login_required(ProfileEditEmailView.as_view())
