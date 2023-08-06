from dcbase.lib.profileEditor import ProfileEditor
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy


def profile_model():
    def _wrapper(profile_class):
        ProfileEditor.register_profile_model(profile_class)
        return profile_class
    return _wrapper

