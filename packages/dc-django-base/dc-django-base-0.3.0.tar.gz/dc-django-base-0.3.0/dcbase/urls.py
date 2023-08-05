from dcbase.views.profile.profile import profileView
from dcbase.views.profile.profileEditEmail import profileEditEmailView
from dcbase.views.profile.profileEditGeneral import profileEditGeneralView
from dcbase.views.profile.profileEditPassword import profileEditPasswordView
from dcbase.views.profile.profileEditSetPassword import profileEditSetPasswordView
from dcbase.views.profile.profileEditSocial import profileEditSocialView
from dcbase.views.profile.profileEditUser import profileEditUserView
from dcbase.views.profile.profileUser import profileUserView
from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/password/set/$', profileEditSetPasswordView, name='account_profile_edit_set_password'),
    url(r'^accounts/password/change/$', profileEditPasswordView, name='account_profile_edit_password'),
    url(r'^accounts/email/$', profileEditEmailView, name='account_email'),
    url(r'^accounts/social/connections/$', profileEditSocialView, name='socialaccount_connections'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', profileView, name='account_profile'),
    url(r'^accounts/profile/edit/$', profileEditUserView, name='account_profile_edit'),
    url(r'^accounts/profile/edit/general/$', profileEditGeneralView, name='account_profile_edit_general'),
    url(r'^accounts/user/(?P<username>.*)/', profileUserView, name='account_profile_user'),
]
