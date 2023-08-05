__author__ = 'cenk'

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class RoleAuthenticateBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def get_role_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings that this user has through his/her
        role groups. Here the parent does not has perm however the children has according to role.

        :param user_obj: current user
        :param obj: which object user want to access
        :return: user_obj with role permissions
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        if not hasattr(user_obj, '_role_perm_cache'):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                user_group_ids = user_obj.roles.all().values_list('id', flat=True)
                perms = Permission.objects.filter(**{"group__in": user_group_ids})
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            user_obj._role_perm_cache = set("%s.%s" % (ct, name) for ct, name in perms)
        return user_obj._role_perm_cache


    def get_all_permissions(self, user_obj, obj=None):
        """
        :param user_obj: current user
        :param obj: which object user want to access
        :return: user with all permissions
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set(
                "%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related())
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
            user_obj._perm_cache.update(self.get_role_permissions(user_obj))

        return user_obj._perm_cache

