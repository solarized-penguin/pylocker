from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from .auth_client import AuthClient, create_auth_client
from .tokens import Token
from .users_schemas import UserInfo, UserSignUp
from ..core import Settings, get_settings

router = APIRouter()


@router.post(
    '/sign-up',
    status_code=201
)
async def sign_up(
        user: UserSignUp = Depends(UserSignUp.as_form),
        client: AuthClient = Depends(create_auth_client),
        settings: Settings = Depends(get_settings)
) -> JSONResponse:
    user_info: UserInfo = client.register_user(user, settings.standard_user_roles)
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
    status_code=200
)
async def sign_in(
        auth_form: OAuth2PasswordRequestForm = Depends(),
        client: AuthClient = Depends(create_auth_client)
) -> Token:
    return client.login_user(
        email=auth_form.username,
        password=auth_form.password
    )
