from http import HTTPStatus

import pytest

from .test_registration_login import login_user

pytestmark = pytest.mark.asyncio


async def test_history(make_get_request):
    """Тест на получение истории входа в аккаунт"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}

    response = await make_get_request('/history', {}, headers, 'get')

    assert response.status == HTTPStatus.OK
    assert 'history' in response.body


async def test_change_login(psql_client, make_get_request):
    """Тест на изменение логина"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {
        'login': 'new_login',
        'password': 'SuperTest228!'
        }
    psql_query = "SELECT * FROM users WHERE login='new_login'"

    response = await make_get_request('/change_login', params, headers)
    psql_response = await psql_client.fetchrow(psql_query)

    assert response.status == HTTPStatus.OK
    assert response.body == 'Login changed'
    assert psql_response


async def test_change_login_wrong(psql_client, make_get_request):
    """Тест на изменение логина с неправильным паролем"""
    access_token, _ = await login_user(make_get_request, 4)
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {
        'login': 'new_login',
        'password': 'SuperTest2281!'
        }

    response = await make_get_request('/change_login', params, headers)

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body == 'Wrong password'


async def test_change_password_wrong(make_get_request):
    """Тест на изменение пароля с неправильным паролем"""
    access_token, _ = await login_user(make_get_request, 5)
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {
        'old_password': 'SuperTest2281!',
        'new_password': 'SuperTestNew228!'
        }

    response = await make_get_request('/change_password', params, headers)

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body == 'Wrong password'


async def test_change_password(psql_client, make_get_request):
    """Тест на изменение пароля"""
    access_token, _ = await login_user(make_get_request, 5)
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {
        'old_password': 'SuperTest228!',
        'new_password': 'SuperTestNew228!'
        }

    response = await make_get_request('/change_password', params, headers)

    assert response.status == HTTPStatus.OK
    assert response.body == 'Password changed'
