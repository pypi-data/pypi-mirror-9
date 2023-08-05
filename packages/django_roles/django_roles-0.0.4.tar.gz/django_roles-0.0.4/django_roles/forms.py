from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

from django_roles.models import DRUser


__author__ = 'cenk'


class DRUserChangeForm(UserChangeForm):
    class Meta:
        model = DRUser
        fields = '__all__'


class DRUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    class Meta:
        model = DRUser
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            DRUser._default_manager.get(username=username)
        except DRUser.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )


class DRAdminPasswordChangeForm(AdminPasswordChangeForm):
    pass
