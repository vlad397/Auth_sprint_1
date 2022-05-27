import uuid
from http import HTTPStatus

import pytest

from .test_registration_login import login_user

pytestmark = pytest.mark.asyncio


async def get_users_id(psql_client):
    psql_user = "SELECT id, login FROM users"
    psql_response = dict(await psql_client.fetch(psql_user))
    users_dict = {}
    for person in psql_response:
        users_dict[psql_response[person]] = str(person)
    return users_dict


async def get_roles_id(psql_client):
    psql_user = "SELECT id, name FROM roles"
    psql_response = dict(await psql_client.fetch(psql_user))
    roles_dict = {}
    for role in psql_response:
        roles_dict[psql_response[role]] = str(role)
    return roles_dict


async def test_preparations(psql_client, make_get_request):
    """Создание заготовок"""
    # Создадим роль суперадмина и админа
    role_id0 = uuid.uuid4()
    role_id1 = uuid.uuid4()

    psql_role0 = (f"INSERT INTO roles (id, name, description) "
                  f"VALUES ('{role_id0}', 'superadmin', 'God')")
    await psql_client.fetchrow(psql_role0)
    psql_role1 = (f"INSERT INTO roles (id, name, description) "
                  f"VALUES ('{role_id1}', 'admin', 'Admin role')")
    await psql_client.fetchrow(psql_role1)

    # Возьмем тестовых пользователей
    psql_user0 = "SELECT * FROM users WHERE email='test0@gmail.com'"
    psql_response0 = dict(await psql_client.fetchrow(psql_user0))
    user_id0 = str(psql_response0['id'])

    psql_user1 = "SELECT * FROM users WHERE email='test1@gmail.com'"
    psql_response1 = dict(await psql_client.fetchrow(psql_user1))
    user_id1 = str(psql_response1['id'])

    # Дадим тестовым пользователям роли суперадмина и админа
    psql_role_user0 = (f"INSERT INTO roles_users (id, user_id, role_id) "
                       f"VALUES (0, '{user_id0}', '{role_id0}')")
    await psql_client.fetchrow(psql_role_user0)
    psql_role_user1 = (f"INSERT INTO roles_users (id, user_id, role_id) "
                       f"VALUES (1, '{user_id1}', '{role_id1}')")
    await psql_client.fetchrow(psql_role_user1)


async def test_role_create_staff(make_get_request):
    """Тест на создание роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'name': f'user{person}',
            'description': f'user role{person}'
            }

        response = await make_get_request('/role', params, headers)

        assert response.status == HTTPStatus.CREATED
        assert response.body == 'Role created'


async def test_role_create_existed_staff(make_get_request):
    """Тест на создание уже существующей роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'name': 'admin',
            'description': f'user role{person}'
            }

        response = await make_get_request('/role', params, headers)

        assert response.status == HTTPStatus.BAD_REQUEST
        assert response.body == 'Role already exists'


async def test_role_change_staff(psql_client, make_get_request):
    """Тест на изменение роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'name': f'user{person}',
            'description': f'user role{person}ЫЫЫ'
            }
        roles = await get_roles_id(psql_client)
        role_id = roles[f'user{person}']
        psql_role = f"SELECT description FROM roles WHERE name='user{person}'"

        response = await make_get_request(
            f'/role/{role_id}', params, headers, 'put')
        psql_response = dict(await psql_client.fetchrow(psql_role))

        assert response.status == HTTPStatus.OK
        assert response.body == 'Role changed'
        assert psql_response == {'description': f'user role{person}ЫЫЫ'}


async def test_role_change_existed_staff(psql_client, make_get_request):
    """Тест на изменение роли в уже существующую другую роль
    суперадмином и админом"""
    for person in [0, 1]:
        # Попытаемся изменить нулевую роль на существующую первую и наоборот
        num = abs(person - 1)
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'name': f'user{num}',
            'description': f'user role{person}'
            }
        roles = await get_roles_id(psql_client)
        role_id = roles[f'user{person}']

        response = await make_get_request(
            f'/role/{role_id}', params, headers, 'put')

        assert response.status == HTTPStatus.BAD_REQUEST
        assert response.body == 'Role already exists'


async def test_role_change_non_existed_staff(psql_client, make_get_request):
    """Тест на изменение несуществующей роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'name': 'some_role',
            'description': f'user role{person}'
            }
        role_id = uuid.uuid4()

        response = await make_get_request(
            f'/role/{role_id}', params, headers, 'put')

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such role'


async def test_role_delete_staff(psql_client, make_get_request):
    """Тест на удаление роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}

        roles = await get_roles_id(psql_client)
        role_id = roles[f'user{person}']
        psql_role = f"SELECT * FROM roles WHERE name='user{person}'"

        response = await make_get_request(
            f'/role/{role_id}', {}, headers, 'delete')
        psql_response = await psql_client.fetchrow(psql_role)

        assert response.status == HTTPStatus.OK
        assert response.body == 'Role deleted'
        assert not psql_response


async def test_role_delete_non_existed_staff(psql_client, make_get_request):
    """Тест на удаление несуществующей роли суперадмином и админом"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}

        role_id = uuid.uuid4()

        response = await make_get_request(
            f'/role/{role_id}', {}, headers, 'delete')

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such role'


async def test_admin_role_change_staff(psql_client, make_get_request):
    """Тест на отказ суперадмину и админу при изменении защищенных ролей"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        for role in ['superadmin', 'admin']:
            params = {
                'name': role,
                'description': 'some role'
                }
            roles = await get_roles_id(psql_client)
            role_id = roles[role]

            response = await make_get_request(
                f'/role/{role_id}', params, headers, 'put')

            assert response.status == HTTPStatus.BAD_REQUEST
            assert response.body == 'Cannot change this role'


async def test_admin_role_delete_staff(psql_client, make_get_request):
    """Тест на отказ суперадмину и админу при удалении защищенных ролей"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        for role in ['superadmin', 'admin']:
            params = {
                'name': role,
                'description': 'some role'
                }
            roles = await get_roles_id(psql_client)
            role_id = roles[role]

            response = await make_get_request(
                f'/role/{role_id}', params, headers, 'delete')

            assert response.status == HTTPStatus.BAD_REQUEST
            assert response.body == 'Cannot delete this role'


async def test_role_give_superadmin(psql_client, make_get_request):
    """Тест на передачу роли суперадмином обычному юзеру"""
    access_token, _ = await login_user(make_get_request, 0)
    headers = {'Authorization': 'Bearer ' + access_token}
    users = await get_users_id(psql_client)
    roles = await get_roles_id(psql_client)
    user_id = users['test2']
    role_id = roles['admin']

    response = await make_get_request(
        f'/role/{user_id}/{role_id}', headers=headers)

    assert response.status == HTTPStatus.CREATED
    assert response.body == 'Role is given'

    # Убедимся, что нельзя дать ту же роль
    response = await make_get_request(
        f'/role/{user_id}/{role_id}', headers=headers)

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body == 'User already has this role'


async def test_role_give_admin(psql_client, make_get_request):
    """Тест на передачу роли админом обычному юзеру"""
    access_token, _ = await login_user(make_get_request, 1)
    headers = {'Authorization': 'Bearer ' + access_token}
    users = await get_users_id(psql_client)
    roles = await get_roles_id(psql_client)
    user_id = users['test3']
    role_id = roles['admin']

    response = await make_get_request(
        f'/role/{user_id}/{role_id}', headers=headers)

    assert response.status == HTTPStatus.CREATED
    assert response.body == 'Role is given'

    # Убедимся, что нельзя дать ту же роль
    response = await make_get_request(
        f'/role/{user_id}/{role_id}', headers=headers)

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body == 'User already has this role'


async def test_non_existed_role_give_staff(psql_client, make_get_request):
    """Тест на передачу несуществующей роли админом или суперадмином"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        users = await get_users_id(psql_client)
        user_id = users['test3']
        role_id = uuid.uuid4()

        response = await make_get_request(
            f'/role/{user_id}/{role_id}', headers=headers)

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such role'


async def test_role_give_staff_to_nobody(psql_client, make_get_request):
    """Тест на передачу роли админом или суперадмином несуществующему юзеру"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        roles = await get_roles_id(psql_client)
        user_id = uuid.uuid4()
        role_id = roles['admin']

        response = await make_get_request(
            f'/role/{user_id}/{role_id}', headers=headers)

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such user'


async def test_non_existed_role_take_staff(psql_client, make_get_request):
    """Тест на отнятие несуществующей роли админом или суперадмином"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        users = await get_users_id(psql_client)
        user_id = users['test3']
        role_id = uuid.uuid4()

        response = await make_get_request(
            f'/role/{user_id}/{role_id}', {}, headers, 'delete')

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such role'


async def test_role_take_staff_from_nobody(psql_client, make_get_request):
    """Тест на отнятие роли админом или суперадмином несуществующему юзеру"""
    for person in [0, 1]:
        access_token, _ = await login_user(make_get_request, person)
        headers = {'Authorization': 'Bearer ' + access_token}
        roles = await get_roles_id(psql_client)
        user_id = uuid.uuid4()
        role_id = roles['admin']

        response = await make_get_request(
            f'/role/{user_id}/{role_id}', headers=headers)

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == 'No such user'


async def test_casual_user_has_no_rights_to_post_role(make_get_request):
    """Тест на отсутствие права на создание роли у обычного пользователя"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {
            'name': 'user',
            'description': 'user role}'
            }

    response = await make_get_request('/role', params, headers)

    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body == 'You do not have rights'


async def test_casual_user_has_no_rights_to_put_and_delete_role(
    make_get_request
):
    """Тест на отсутствие права на изменение/удаление роли у обычного юзера"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}
    some_id = uuid.uuid4()
    for m_type in ['put', 'delete']:
        params = {
                'name': 'user',
                'description': 'user role}'
                }

        response = await make_get_request(
            f'/role/{some_id}', params, headers, m_type)

        assert response.status == HTTPStatus.FORBIDDEN
        assert response.body == 'You do not have rights'


async def test_casual_user_has_no_rights_to_give_and_take_role(
    make_get_request
):
    """Тест на отсутствие права на отнятие/передачу роли у обычного юзера"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}
    some_id = uuid.uuid4()
    for m_type in ['post', 'delete']:
        response = await make_get_request(
            f'/role/{some_id}/{some_id}', {}, headers, m_type)

        assert response.status == HTTPStatus.FORBIDDEN
        assert response.body == 'You do not have rights'
