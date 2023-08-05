from django import forms
from djinn_profiles.utils import get_userprofile_model


UserProfile = get_userprofile_model()


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
