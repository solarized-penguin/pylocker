from fastapi import APIRouter, Depends

from .auth_client import AuthClient
from .users_schemas import UserRead, UserSignUp

router = APIRouter()


@router.post(
    '/',
    response_model=UserRead,
    status_code=201
)
async def sign_up(
        user: UserSignUp = Depends(UserSignUp.as_form),
        client: AuthClient = Depends(AuthClient)
) -> UserRead:
    return client.register_user(user)
