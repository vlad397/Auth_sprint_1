import uuid
from http import HTTPStatus

import pytest

from .test_registration_login import login_user

pytestmark = pytest.mark.asyncio


async def test_refresh_token(make_get_request):
    """Тест обновления токена"""
    _, refresh_token = await login_user(make_get_request, 0)
    headers = {'Authorization': 'Bearer ' + refresh_token}

    response = await make_get_request('/token_refresh', headers=headers)

    assert response.status == HTTPStatus.OK
    assert 'access_token' in response.body
    assert 'refresh_token' not in response.body


async def test_logout(make_get_request):
    """Тестирование выхода из аккаунта"""
    access_token, _ = await login_user(make_get_request, 0)
    headers = {'Authorization': 'Bearer ' + access_token}

    response = await make_get_request('/logout', headers=headers)

    assert response.status == HTTPStatus.OK
    assert response.body == 'Access token has been revoked'

    # Убедимся, что токен в черном списке
    response = await make_get_request('/logout', headers=headers)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Token has been revoked'}


async def test_logout_refresh(make_get_request):
    """Удаление refresh токена"""
    _, refresh_token = await login_user(make_get_request, 0)
    headers = {'Authorization': 'Bearer ' + refresh_token}

    response = await make_get_request('/logout_refresh', headers=headers)

    assert response.status == HTTPStatus.OK
    assert response.body == 'Refresh token has been revoked'

    # Убедимся, что токен в черном списке
    response = await make_get_request('/logout_refresh', headers=headers)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Token has been revoked'}


async def test_guest_has_no_rights_to_logout(make_get_request):
    """Тест на гостя"""
    response = await make_get_request('/logout')

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_logout_refresh(make_get_request):
    """Тест на гостя"""
    response = await make_get_request('/logout_refresh')

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_post_role(make_get_request):
    """Тест на гостя"""
    params = {'name': '', 'description': ''}
    response = await make_get_request('/role', params)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_put_and_delete_role(make_get_request):
    """Тест на гостя"""
    some_id = uuid.uuid4()
    for m_type in ['put', 'delete']:
        params = {'name': '', 'description': ''}
        response = await make_get_request(
            f'/role/{some_id}', params, method_type=m_type)

        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_take_and_delete_role(make_get_request):
    """Тест на гостя"""
    some_id = uuid.uuid4()
    for m_type in ['', 'delete']:
        response = await make_get_request(
            f'/role/{some_id}/{some_id}', method_type=m_type)

        assert response.status == HTTPStatus.UNAUTHORIZED
        assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_history(make_get_request):
    """Тест на гостя"""
    response = await make_get_request('/history', method_type='get')

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_change_login(make_get_request):
    """Тест на гостя"""
    params = {'login': 'hz', 'password': 'Ololo123!'}
    response = await make_get_request('/change_login', params)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}


async def test_guest_has_no_rights_to_change_password(make_get_request):
    """Тест на гостя"""
    params = {'old_password': 'Ololo123!', 'new_password': 'Ololo123!'}
    response = await make_get_request('/change_password', params)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {'msg': 'Missing Authorization Header'}
