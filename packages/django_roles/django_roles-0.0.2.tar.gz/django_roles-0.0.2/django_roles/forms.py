from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

from django_auth.models import DAuthUser


__author__ = 'cenk'


class DAuthUserChangeForm(UserChangeForm):
    class Meta:
        model = DAuthUser
        fields = '__all__'


class DAuthUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    class Meta:
        model = DAuthUser
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            DAuthUser._default_manager.get(username=username)
        except DAuthUser.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )


class DAuthAdminPasswordChangeForm(AdminPasswordChangeForm):
    pass
