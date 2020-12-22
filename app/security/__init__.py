from fastapi.security import OAuth2PasswordBearer

from ..core.settings import get_settings

security_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/users/sign-in',
    scopes={
        get_settings().standard_user_roles[0]: 'standard user account privileges'
    }
)
