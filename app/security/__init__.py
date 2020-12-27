from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.security.auth_client import AuthClient
from app.security.users_schemas import UserInfo

security_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/users/sign-in'
)


def logged_user(
        request: Request,
        token: str = Depends(security_scheme),
        client: AuthClient = Depends(AuthClient.create_client)
) -> UserInfo:
    """
    Returns id of currently logged user.
    :param request: current request
    :param client: identity provider client
    :param token: access token
    :return: user id
    :rtype: str
    """
    user_info = client.fetch_user_info(token)

    logger.info(
        f'User: {user_info.email} accessed: |{request.method}| => {request.url}'
    )
    return user_info
