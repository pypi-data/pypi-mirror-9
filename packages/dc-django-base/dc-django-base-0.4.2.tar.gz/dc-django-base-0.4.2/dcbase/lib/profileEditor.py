from collections import namedtuple, OrderedDict
from dcbase.lib.navLink import NavLink
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class ProfileModel(object):
    def __init__(self, model):
        self.model = model
        self.editUrl = ''
        self.name = ''

class ProfileEditor(object):
    _profileModels = OrderedDict()

    @classmethod
    def add_profile_edit_context(cls, context, navName, panelName):
        navLinks = [
            NavLink(_('User'), reverse('account_profile_edit')),
            NavLink(_('Change Password'), reverse('account_change_password')),
            NavLink(_('E-mail'), reverse('account_email')),
            NavLink(_('Social Accounts'), reverse('socialaccount_connections')),
        ]
        for profileModel in cls.get_profile_models():
            navLinks.append(NavLink(profileModel.name, profileModel.editUrl))

        context['profileNavLinks'] = navLinks
        context['selectedProfileNavLink'] = navName
        context['profilePanelHeading'] = panelName

    @classmethod
    def register_profile_model(cls, model):
        if model in cls._profileModels:
            return
        cls._profileModels[model] = ProfileModel(model)

    @classmethod
    def register_profile_view(cls, model, profile_url, nav_name):
        cls.register_profile_model(model)
        profileModel = cls._profileModels[model]
        profileModel.editUrl = profile_url
        profileModel.name = nav_name

    @classmethod
    def get_profile_models(cls):
        return cls._profileModels.values()

