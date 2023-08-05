from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView


class ProfileUserView(TemplateView):
    template_name = 'dcbase/profile.html'

    def get_context_data(self, username, **kwargs):
        user = get_object_or_404(User, username=username)
        kwargs['profileUser'] = user
        return kwargs

profileUserView = ProfileUserView.as_view()
