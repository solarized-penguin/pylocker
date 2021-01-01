from typing import Dict, Any

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.auth_client.auth_client import AuthClient
from app.core import Settings

security_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/users/sign-in'
)


def logged_user(
        request: Request,
        token: str = Depends(security_scheme),
        settings: Settings = Depends(Settings.get)
) -> str:
    """
    Returns id of currently logged user.
    :param request: current request
    :param token: access token
    :param settings: application settings
    :return: user id
    :rtype: str
    """

    decoded_token: Dict[str, Any] = \
        jwt.decode(
            token,
            settings.jwt_signing_key.get_secret_value(),
            algorithms=settings.jwt_algorithms,
            audience=settings.app_id.get_secret_value()
        )
    email: str = decoded_token['email']

    logger.info(
        f'User: {email} accessed: |{request.method}| => {request.url}'
    )
    return email
