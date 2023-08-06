from django.contrib.auth.models import Group, Permission, _user_get_all_permissions, _user_has_perm, _user_has_module_perms
from django.db.models.manager import EmptyManager
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class SuperUser(object):
    id = None
    pk = None
    username = 'SuperUser'
    is_staff = True
    is_active = True
    is_superuser = True
    _groups = EmptyManager(Group)
    _user_permissions = EmptyManager(Permission)

    def __init__(self):
        pass

    def __str__(self):
        return 'SuperUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def save(self):
        raise NotImplementedError("Django doesn't provide a DB representation for SuperUser.")

    def delete(self):
        raise NotImplementedError("Django doesn't provide a DB representation for SuperUser.")

    def set_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for SuperUser.")

    def check_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for SuperUser.")

    def _get_groups(self):
        return self._groups
    groups = property(_get_groups)

    def _get_user_permissions(self):
        return self._user_permissions
    user_permissions = property(_get_user_permissions)

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj=obj)

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, module):
        return _user_has_module_perms(self, module)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_username(self):
        return self.username
