from allauth.account.views import LogoutView
from django.http import JsonResponse
from django.utils.translation import ugettext as _


class DcLogoutView(LogoutView):
    def post(self, *args, **kwargs):
        super().post(*args, **kwargs)
        return JsonResponse({'action': 'redirect', 'url': self.get_redirect_url()})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['submit_text'] = _('Sign Out')
        data['submit_style'] = 'danger'
        return data
