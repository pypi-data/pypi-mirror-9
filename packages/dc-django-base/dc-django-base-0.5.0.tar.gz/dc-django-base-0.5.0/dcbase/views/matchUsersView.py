from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.generic import View
from django_gravatar.helpers import get_gravatar_url


class MatchUsersView(View):
    def get(self, request, **kwargs):
        queryString = request.GET.get('q')
        if not queryString:
            raise PermissionDenied()

        out = []
        users = User.objects.filter(username__icontains=queryString).order_by('username')[:10]
        for user in users:
            out.append({
                'value': user.username,
                'avatar_url': get_gravatar_url(user.email, size=25)
            })
        return JsonResponse(out, safe=False)


matchUsersView = MatchUsersView.as_view()

