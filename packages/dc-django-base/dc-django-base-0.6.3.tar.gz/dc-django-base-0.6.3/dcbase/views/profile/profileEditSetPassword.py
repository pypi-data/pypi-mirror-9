from allauth.account.views import PasswordSetView
from dcbase.lib.profileEditor import ProfileEditor
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _


class ProfileEditSetPasswordView(PasswordSetView):
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ProfileEditor.add_profile_edit_context(kwargs, _('Change Password'), _('Set Password'))
        return kwargs

profileEditSetPasswordView = login_required(ProfileEditSetPasswordView.as_view())
