from enum import Enum


class PermissionRoles(str, Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "superadmin"


def is_admin(user) -> bool:
    """Проверка роли админа"""
    return True if PermissionRoles.ADMIN in user.roles_list() else False


def is_super_admin(user) -> bool:
    """Проверка роли суперадмина"""
    return True if PermissionRoles.SUPER_ADMIN in user.roles_list() else False


def admin_affects_on_superadmin(user1, user2) -> bool:
    """Проверка действий админа к суперадмину"""
    if PermissionRoles.SUPER_ADMIN in user1.roles_list():
        return False
    if (
        PermissionRoles.SUPER_ADMIN not in user1.roles_list()
        and PermissionRoles.SUPER_ADMIN in user2.roles_list()
    ):
        return True
    return False
