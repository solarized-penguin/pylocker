from typing import List

from fusionauth.fusionauth_client import FusionAuthClient
from fusionauth.rest_client import ClientResponse

from .tokens import Token
from .users_schemas import UserRegistrationForm, UserInfo, \
    RegistrationRequest, AppRegistrationForm, UserSignUp, UserSignIn
from ..core.settings import get_settings, Settings
from ..errors import UserSignUpError, UserSignInError


class AuthClient:
    def __init__(self) -> None:
        self._settings: Settings = get_settings()
        self._client: FusionAuthClient = FusionAuthClient(
            self._settings.api_key.get_secret_value(),
            self._settings.auth_provider_url
        )

    def register_user(self, user: UserSignUp, roles: List[str]) -> UserInfo:
        request = RegistrationRequest(
            registration=AppRegistrationForm(
                applicationId=self._settings.app_id.get_secret_value(),
                roles=roles
            ),
            user=UserRegistrationForm(
                email=user.email,
                fullName=user.fullName,
                mobilePhone=user.mobilePhone,
                birthDate=user.birthDate.strftime('%Y-%m-%d')
                if user.birthDate is not None else None,
                password=user.password1.get_secret_value()
            )
        ).dict(exclude_none=True)

        response: ClientResponse = self._client.register(request)

        if response.was_successful():
            return UserInfo(**response.success_response['user'])
        else:
            raise UserSignUpError(response.error_response)

    def login_user(self, user: UserSignIn) -> Token:
        response = self._client \
            .exchange_user_credentials_for_access_token(
            username=user.email,
            password=user.password.get_secret_value(),
            client_id=self._settings.client_id.get_secret_value(),
            client_secret=self._settings.client_secret.get_secret_value()
        )

        if response.was_successful():
            return Token(**response.success_response)
        else:
            raise UserSignInError(response.error_response)
