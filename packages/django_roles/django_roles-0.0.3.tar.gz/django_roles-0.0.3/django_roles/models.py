from django_roles.managers import DRUserManager

__author__ = 'cenk'

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from django.contrib.auth.models import AbstractUser


class DRAbstractUser(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    objects = DRUserManager()

    class Meta:
        abstract = True
        verbose_name = "User"
        verbose_name_plural = "Users"


class DRUser(DRAbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        verbose_name = "User"
        verbose_name_plural = "Users"


class DRUserRole(MPTTModel):
    name = models.CharField(_('Role Name'), max_length=200)
    parent = TreeForeignKey('self', blank=True, null=True, related_name="children", verbose_name='Parent Role')
    groups = models.ManyToManyField(Group, verbose_name=_('Groups'), null=True, blank=True)
    status = models.BooleanField(default=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('User Roles'), blank=True,
                                   related_name="roles")


    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

    def __str__(self):
        return self.name