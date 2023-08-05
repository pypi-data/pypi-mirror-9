from django.contrib.auth.admin import UserAdmin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django_roles.forms import DRUserChangeForm, DRAdminPasswordChangeForm
from django_roles.forms import DRUserCreationForm


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
__author__ = 'cenk'


class DRUserAdmin(UserAdmin):
    form = DRUserChangeForm
    add_form = DRUserCreationForm
    change_password_form = DRAdminPasswordChangeForm

