from copy import deepcopy
from datetime import datetime, date
from typing import Dict, List, Any, Callable, Generator

import pytest
from assertpy import assert_that
from databases import Database
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from requests import Response

from app import create_app
from app.core import get_db
from app.schemas.enums import UsernameStatus, TwoFactorDelivery
from app.schemas.users import UserSignUp, UserInfo
from app.schemas.validations import UserValidationRules


@pytest.fixture(scope='function')
def client(db: Database) -> Generator[TestClient, None, None]:
    app: FastAPI = create_app()

    def _get_db() -> Database: return db

    app.dependency_overrides[get_db] = _get_db

    client: TestClient = TestClient(app)
    yield client


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
        'app.routers.users_router.AuthClient.register_user',
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

    def test__full_name_filled_incorrectly__returns_400_and_message(
            self, client: TestClient,
            assertion_extensions: Callable[[None], None]
    ) -> None:
        request_data: Dict[str, Any] = deepcopy(test_user_sign_up)

        request_data['fullName'] = 'JustOneName'

        response: Response = client.post(
            '/users/sign-up',
            data=request_data,
            headers=form_headers
        )

        assert_that(response.json()) \
            .is_validation_message_correct(
            UserValidationRules.full_name_error_message
        )

    def test__mobile_phone_filled_incorrectly__returns_400_and_message(
            self, client: TestClient,
            assertion_extensions: Callable[[None], None]
    ) -> None:
        request_data: Dict[str, Any] = deepcopy(test_user_sign_up)

        request_data['mobilePhone'] = '123.456$789'

        response: Response = client.post(
            '/users/sign-up',
            data=request_data,
            headers=form_headers
        )

        assert_that(response.json()) \
            .is_validation_message_correct(
            UserValidationRules.mobile_error_message
        )

    def test__password_filled_incorrectly__returns_400_and_message(
            self, client: TestClient,
            assertion_extensions: Callable[[None], None]
    ) -> None:
        request_data: Dict[str, Any] = deepcopy(test_user_sign_up)

        request_data['password1'] = 'incorrect_password'
        request_data['password2'] = request_data['password1']

        response: Response = client.post(
            '/users/sign-up',
            data=request_data,
            headers=form_headers
        )

        assert_that(response.json()) \
            .is_validation_message_correct(
            UserValidationRules.password_error_message
        )

    def test__passwords_do_not_match__returns_400_and_message(
            self, client: TestClient,
            assertion_extensions: Callable[[None], None]
    ) -> None:
        request_data: Dict[str, Any] = deepcopy(test_user_sign_up)

        request_data['password1'] = 'pa$Sw0rd'
        request_data['password2'] = 'incorrect_repeat'

        response: Response = client.post(
            '/users/sign-up',
            data=request_data,
            headers=form_headers
        )

        assert_that(response.json()) \
            .is_validation_message_correct(
            UserValidationRules.passwords_not_match_error_message
        )
