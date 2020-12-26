from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.security.auth_client import AuthClient
from app.security.users_schemas import UserInfo

security_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/users/sign-in'
)


def logged_user(
        token: str = Depends(security_scheme),
        client: AuthClient = Depends(AuthClient.create_client)
) -> UserInfo:
    """
    Returns id of currently logged user.
    :param client: identity provider client
    :param token: access token
    :return: user id
    :rtype: str
    """
    return client.fetch_user_info(token)
