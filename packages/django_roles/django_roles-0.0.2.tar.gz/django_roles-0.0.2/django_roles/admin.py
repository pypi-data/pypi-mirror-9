from django.contrib.auth.admin import UserAdmin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django_auth.forms import DAuthUserChangeForm, DAuthUserCreationForm, DAuthAdminPasswordChangeForm


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
__author__ = 'cenk'


class DAuthUserAdmin(UserAdmin):
    form = DAuthUserChangeForm
    add_form = DAuthUserCreationForm
    change_password_form = DAuthAdminPasswordChangeForm

