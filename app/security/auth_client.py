from fastapi.security import OAuth2PasswordBearer
from fusionauth.fusionauth_client import FusionAuthClient
from fusionauth.rest_client import ClientResponse
from passlib.context import CryptContext

from .users import UserWrite, UserRead, UserRegistrationRequest, Registration
from ..core.settings import get_settings, Settings


class AuthClient:
    def __init__(self) -> None:
        self._settings: Settings = get_settings()
        self._context = CryptContext(
            schemes=[self._settings.pswd_algorithm],
            depreciated='auto'
        )
        self._oauth2_schema: OAuth2PasswordBearer \
            = OAuth2PasswordBearer(tokenUrl=self._settings.token_url)

    def __enter__(self):
        self._client: FusionAuthClient \
            = FusionAuthClient(self._settings.secret_key, self._settings.auth_provider_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            raise Exception("auth client error - TODO")

    def register_user(self, user: UserWrite) -> UserRead:
        request = UserRegistrationRequest(
            registrations=[
                Registration(
                    applicationId=self._settings.app_id.get_secret_value(),
                    roles=[self._settings.standard_user_role]
                )
            ],
            user=user.dict()
        )
        response: ClientResponse = self._client.register(request)

        if response.was_successful():
            result: UserRead = UserRead(**response.success_response)
            return result
        else:
            error_response = response.error_response
