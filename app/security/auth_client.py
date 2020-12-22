from __future__ import annotations

from fastapi.security import OAuth2PasswordBearer
from fusionauth.fusionauth_client import FusionAuthClient
from fusionauth.rest_client import ClientResponse
from passlib.context import CryptContext

from .users_schemas import UserRegistrationForm, UserRead, RegistrationRequest, AppRegistrationForm, UserSignUp
from ..core.settings import get_settings, Settings
from ..errors import UserRegistrationError


class AuthClient:
    def __init__(self) -> None:
        self._settings: Settings = get_settings()
        self._context = CryptContext(
            schemes=[self._settings.pswd_algorithm]
        )
        self._oauth2_schema: OAuth2PasswordBearer \
            = OAuth2PasswordBearer(tokenUrl=self._settings.token_url)
        self._client: FusionAuthClient = FusionAuthClient(
            self._settings.api_key.get_secret_value(),
            self._settings.auth_provider_url
        )

    def register_user(self, user: UserSignUp) -> UserRead:
        request = RegistrationRequest(
            registration=AppRegistrationForm(
                applicationId=self._settings.app_id.get_secret_value(),
                roles=[self._settings.standard_user_role]
            ),
            user=UserRegistrationForm(
                email=user.email,
                fullName=user.fullName,
                mobilePhone=user.mobilePhone,
                birthDate=user.birthDate.strftime('%Y-%m-%d') if user.birthDate is not None else None,
                password=user.password1.get_secret_value()
            )
        ).dict(exclude_none=True)

        response: ClientResponse = self._client.register(request)

        if response.was_successful():
            result: UserRead = UserRead(**response.success_response['user'])
            return result
        else:
            raise UserRegistrationError(
                error_code=response.status,
                error_message=response.error_response
            )
