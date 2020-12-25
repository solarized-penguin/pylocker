from datetime import datetime, date
from typing import Dict, List, Any, Callable

from assertpy import assert_that
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from requests import Response

from app.security.enum_models import UsernameStatus, TwoFactorDelivery
from app.security.users_schemas import UserSignUp, UserInfo

test_user_sign_up: Dict[str, Any] = {
    'email': 'test@domain.com',
    'fullName': 'FirstName LastName',
    'mobilePhone': '123-456-789',
    'password1': 'QwertY123',
    'password2': 'QwertY123',
    'imageUrl': 'https://www.image-host.com/avatar.png',
    'birthDate': date(2000, 1, 1),
}

test_user_info: Dict[str, Any] = {
    'email': 'test@domain.com',
    'fullName': 'FirstName LastName',
    'mobilePhone': '123-456-789',
    'id': 'test-user-id',
    'imageUrl': 'https://www.image-host.com/avatar.png',
    'birthDate': date(2000, 1, 1),
    'active': True,
    'passwordLastUpdateInstant': datetime.now(),
    'usernameStatus': UsernameStatus.ACTIVE.value,
    'twoFactorDelivery': TwoFactorDelivery.NONE.value,
    'verified': True,
    'tenantId': 'test-tenant-id',
    'passwordChangeRequired': False,
    'insertInstant': datetime.now().timestamp(),
}

form_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}


def mock_register_user(
        mocker: MockerFixture, user_info: Dict[str, Any]
) -> None:
    def _register_user(
            self: Any, user: UserSignUp, roles: List[str]
    ) -> UserInfo:
        if not user or not roles:
            raise ValueError('Some values were passed incorrectly!')
        return UserInfo(**user_info)

    mocker.patch(
        'app.security.users_router.AuthClient.register_user',
        _register_user
    )


class TestSignUp:

    def test__model_filled_correctly__registration_successful(
            self, mocker: MockerFixture, client: TestClient,
            assertion_extensions: Callable[[None], None]
    ) -> None:
        mock_register_user(mocker, user_info=test_user_info)

        response: Response = client.post(
            '/users/sign-up',
            data=test_user_sign_up,
            headers=form_headers
        )

        assert_that(response.status_code).is_successful_status_code()
