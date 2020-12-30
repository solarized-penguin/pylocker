from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.auth_client.auth_client import AuthClient
from app.core import Settings
from app.schemas.tokens import Token
from app.schemas.users import UserInfo, UserSignUp

router: APIRouter = APIRouter()


@router.post(
    '/sign-up',
    status_code=201
)
async def sign_up(
        user: UserSignUp = Depends(UserSignUp.as_form),
        client: AuthClient = Depends(AuthClient.create_client),
        settings: Settings = Depends(Settings.get)
) -> JSONResponse:
    """
    Create user account and register it with this application
    :param settings: application settings
    :param client: auth service client
    :type user: UserSignUp
    :returns: 201 - account created
    """
    user_info: UserInfo = client.register_user(user, settings.standard_user_roles)

    logger.info(f"Account: '{user_info.email}' created successfully.")

    return JSONResponse(
        content={
            'message': f"Registration process for user with email: "
                       f"'{user_info.email}' concluded successfully"
        },
        status_code=201
    )


@router.post(
    '/sign-in',
    response_model=Token,
    status_code=200,
    include_in_schema=False
)
async def sign_in(
        auth_form: OAuth2PasswordRequestForm = Depends(),
        client: AuthClient = Depends(AuthClient.create_client)
) -> Token:
    """
    Obtain access token by providing email and account password
    :param auth_form: login form
    :param client: auth service client
    :return: access token
    :rtype: Token
    """
    token: Token = client.login_user(
        email=auth_form.username,
        password=auth_form.password
    )

    logger.info(f"User: '{auth_form.username}' logged successfully.")

    return token
