from dcbase.models import UserProfile
from django.forms import ModelForm


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['language']
