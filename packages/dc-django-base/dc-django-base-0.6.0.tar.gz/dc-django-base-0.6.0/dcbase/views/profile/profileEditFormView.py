from dcbase.lib.profileEditor import ProfileEditor
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView


class ProfileEditFormView(UpdateView):
    template_name = 'dcbase/profile_edit.html'
    form_class = None
    profile_nav_name = 'UNKNOWN PROFILE SETTINGS'
    profile_panel_name = 'UNKNOWN PROFILE SETTINGS'
    profile_edit_url = reverse_lazy('account_profile_edit')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ProfileEditor.add_profile_edit_context(kwargs, self.profile_nav_name, self.profile_panel_name)
        return kwargs

    def get_object(self, queryset=None):
        return self.form_class.Meta.model.objects.get(user = self.request.user)
        # return self.request.user

    def get_success_url(self):
        return self.profile_edit_url

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Successfully updated {}').format(self.profile_panel_name))
        return response
