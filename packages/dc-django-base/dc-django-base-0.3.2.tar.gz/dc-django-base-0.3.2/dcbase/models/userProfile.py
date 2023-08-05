from dcbase.decorator.profileModel import profile_model
from dcbase.lib.profileEditor import ProfileEditor
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models import Model, OneToOneField, CharField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import ugettext_lazy as _, LANGUAGE_SESSION_KEY


@profile_model()
class UserProfile(Model):
    user = OneToOneField(User, related_name='profile')
    language = CharField(_('Language'), max_length=10, choices=settings.LANGUAGES, default='en')

    @property
    def languageName(self):
        return dict(settings.LANGUAGES)[self.language]


@receiver(user_logged_in)
def login_handler(sender, request, user, **kwargs):
    request.session[LANGUAGE_SESSION_KEY] = user.profile.language

@receiver(post_save, sender = User)
def createUserProfile(sender, instance, created, **kwargs):
    if not created:
        return

    for profileModel in ProfileEditor.get_profile_models():
        profileModel.model.objects.create(user = instance)
    instance.profile.language = translation.get_language()
    instance.profile.save()

