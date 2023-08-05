from dcbase.decorator.profileFormView import profile_form_view
from dcbase.forms.userProfile import UserProfileForm
from dcbase.views.profile.profileEditFormView import ProfileEditFormView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _, LANGUAGE_SESSION_KEY


@profile_form_view()
class ProfileEditGeneralView(ProfileEditFormView):
    form_class = UserProfileForm
    profile_nav_name = _('General')
    profile_panel_name = _('General Settings')
    profile_edit_url = reverse_lazy('account_profile_edit_general')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session[LANGUAGE_SESSION_KEY] = self.request.POST['language']
        return response

profileEditGeneralView = login_required(ProfileEditGeneralView.as_view())

