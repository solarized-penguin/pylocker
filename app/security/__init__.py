from fastapi.security import OAuth2PasswordBearer

security_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/users/sign-in'
)
