from django import template
from django.core.urlresolvers import reverse


register = template.Library()

@register.simple_tag
def userNameLink(user):
    username = user.username
    profile_url = reverse('account_profile_user', kwargs = {'username': username})
    return '<a class="userNameLink" href="{link}">{username}</a>'.format(link=profile_url, username=username)

