from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr, HttpUrl


class UserSignUp(BaseModel):
    email: EmailStr
    password1: SecretStr
    password2: SecretStr
    fullName: Optional[str] = None
    mobilePhone: Optional[str] = None
    imageUrl: Optional[HttpUrl] = None
    birthDate: Optional[date] = None

    class Config:
        orm_mode = True


class UserSignIn(BaseModel):
    username: EmailStr
    password: SecretStr

    class Config:
        orm_mode = True
