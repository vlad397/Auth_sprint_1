from xmlrpc.client import Boolean


def is_admin(user) -> bool:
    """Проверка роли админа"""
    if 'admin' in user.roles_list():
        return True
    return False


def is_super_admin(user) -> bool:
    """Проверка роли суперадмина"""
    if 'superadmin' in user.roles_list():
        return True
    return False