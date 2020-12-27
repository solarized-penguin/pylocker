from __future__ import annotations

from typing import List

from fusionauth.fusionauth_client import FusionAuthClient
from fusionauth.rest_client import ClientResponse

from .tokens import Token
from .users_schemas import UserRegistrationForm, UserInfo, RegistrationRequest, \
    AppRegistrationForm, UserSignUp
from ..core.settings import Settings
from ..errors import UserSignUpError, UserSignInError, UserInfoNotFoundError


class AuthClient:
    """
    Provides a way to communicate with authentication and authorization service.
    """

    def __init__(self) -> None:
        self._settings: Settings = Settings.get()
        self._client: FusionAuthClient = FusionAuthClient(
            self._settings.api_key.get_secret_value(),
            self._settings.auth_provider_url
        )

    def register_user(self, user: UserSignUp, roles: List[str]) -> UserInfo:
        """
        Creates new user account and registers it with selected application.
        :rtype: UserInfo
        """
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
                password=user.password1.get_secret_value(),
                imageUrl=user.imageUrl
            )
        ).dict(exclude_none=True)

        response: ClientResponse = self._client.register(request)

        if response.was_successful():
            return UserInfo(**response.success_response['user'])
        else:
            raise UserSignUpError(response.error_response)

    def login_user(self, email: str, password: str) -> Token:
        """
        Obtains access token - password grant type.
        :rtype: Token
        """
        response = self._client.exchange_user_credentials_for_access_token(
            username=email,
            password=password,
            client_id=self._settings.client_id.get_secret_value(),
            client_secret=self._settings.client_secret.get_secret_value()
        )

        if response.was_successful():
            return Token(**response.success_response)
        else:
            raise UserSignInError(response.error_response)

    def fetch_user_info(self, access_token: str) -> UserInfo:
        """
        Fetches info about user from valid access token.
        :param access_token: access token obtained after signing in
        :return: information about logged user
        :rtype: UserInfo
        """
        response: ClientResponse = self._client.retrieve_user_using_jwt(access_token)

        if response.was_successful():
            return UserInfo(**response.success_response['user'])
        else:
            raise UserInfoNotFoundError(
                error_code=response.status,
                error_message=response.error_response
            )

    @classmethod
    def create_client(cls) -> AuthClient:
        """
        Returns new instance of self.
        :rtype: AuthClient
        """
        return AuthClient()
