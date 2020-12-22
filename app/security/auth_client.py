from __future__ import annotations

from typing import Any

from fastapi.security import OAuth2PasswordBearer
from fusionauth.fusionauth_client import FusionAuthClient
from fusionauth.rest_client import ClientResponse
from passlib.context import CryptContext
from pydantic import SecretStr

from .users_schemas import UserRead, UserRegistrationRequest, Registration, UserWrite
from ..core.settings import get_settings, Settings
from ..errors import UserRegistrationError, UserNotFoundError


class AuthClient:
    def __init__(self) -> None:
        self._settings: Settings = get_settings()
        self._context = CryptContext(
            schemes=[self._settings.pswd_algorithm]
        )
        self._oauth2_schema: OAuth2PasswordBearer \
            = OAuth2PasswordBearer(tokenUrl=self._settings.token_url)

    def __enter__(self) -> AuthClient:
        self._client: FusionAuthClient \
            = FusionAuthClient(
            self._settings.api_key.get_secret_value(), self._settings.auth_provider_url
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type:
            raise Exception("auth client error - TODO")

    def register_user(self, email: str, password: SecretStr) -> UserRead:
        # TODO: remove try except after debugging
        try:
            request = UserRegistrationRequest(
                registrations=[
                    Registration(
                        applicationId=self._settings.app_id.get_secret_value(),
                        roles=[self._settings.standard_user_role]
                    )
                ],
                user=UserWrite(email=email, password=password.get_secret_value())
            ).dict()
            response: ClientResponse = self._client.register(request)

            if response.was_successful():
                result: UserRead = UserRead(**response.success_response)
                return result
            else:
                error_response = response.error_response
                raise UserRegistrationError(
                    error_code=error_response.status_code,
                    error_message=error_response
                )
        except Exception as e:
            print(e)
            raise Exception("UPS DOESN'T WORK ;(")

    def fetch_user_by_email(self, email: str) -> UserRead:
        response: ClientResponse = self._client.retrieve_user_by_username(email)

        if response.was_successful():
            result: UserRead = UserRead(**response.success_response)
            return result
        else:
            raise UserNotFoundError(
                error_message=dict(
                    message=f"User with email '{email}' doesn't exists!"
                )
            )
