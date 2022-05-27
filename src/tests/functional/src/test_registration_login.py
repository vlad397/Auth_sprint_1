from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def login_user(make_get_request, number: int):
    params = {
        'email': f'test{number}@gmail.com',
        'password': 'SuperTest228!'
        }

    response = await make_get_request('/login', params)

    access_token = response.body['access_token']
    refresh_token = response.body['refresh_token']

    return access_token, refresh_token


async def test_register(psql_client, make_get_request):
    """Проверка регистрации"""

    psql_query = "SELECT * FROM users WHERE email='test0@gmail.com'"
    # Создадим сразу 6 пользователей
    for num in reversed(range(6)):
        params = {
            'first_name': f'test{num}',
            'second_name': f'test{num}',
            'login': f'test{num}',
            'email': f'test{num}@gmail.com',
            'password': 'SuperTest228!'
            }

        response = await make_get_request('/register', params)
    psql_response = dict(await psql_client.fetchrow(psql_query))

    assert response.status == HTTPStatus.CREATED
    assert psql_response['email'] == 'test0@gmail.com'


async def test_login(make_get_request):
    """Проверка входа в аккаунт"""

    params = {
        'email': 'test0@gmail.com',
        'password': 'SuperTest228!'
        }

    response = await make_get_request('/login', params)

    assert response.status == HTTPStatus.OK
    assert 'access_token' in response.body
    assert 'refresh_token' in response.body


async def test_login_wrong_password(make_get_request):
    """Проверка входа в аккаунт с неправильным паролем"""

    params = {
        'email': 'test0@gmail.com',
        'password': 'SuperTest2281!'
        }

    response = await make_get_request('/login', params)

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body == 'Wrong password'


async def test_login_wrong_email(make_get_request):
    """Проверка входа в аккаунт с неправильной почтой"""

    params = {
        'email': 'test100@gmail.com',
        'password': 'SuperTest228!'
        }

    response = await make_get_request('/login', params)

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body == 'No such user'
