from dcbase.lib.profileEditor import ProfileEditor
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy


def profile_form_view():
    def _wrapper(profile_class):
        if hasattr(profile_class, 'form_class') and \
                hasattr(profile_class.form_class, 'Meta') and \
                hasattr(profile_class.form_class.Meta, 'model'):
            model = profile_class.form_class.Meta.model
        else:
            raise ImproperlyConfigured('User Profile class [{}] must have model form class'.format(profile_class.__name__))

        ProfileEditor.register_profile_view(model, profile_class.profile_edit_url, profile_class.profile_nav_name)
        return profile_class
    return _wrapper

