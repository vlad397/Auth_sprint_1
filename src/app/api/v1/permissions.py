A = 'admin'
SA = 'superadmin'


def is_admin(user) -> bool:
    """Проверка роли админа"""
    if A in user.roles_list():
        return True
    return False


def is_super_admin(user) -> bool:
    """Проверка роли суперадмина"""
    if SA in user.roles_list():
        return True
    return False


def admin_affects_on_superadmin(user1, user2) -> bool:
    """Проверка действий админа к суперадмину"""
    if SA in user1.roles_list() and SA in user2.roles_list():
        return False
    if SA not in user1.roles_list() and SA in user2.roles_list():
        return True
    return True
