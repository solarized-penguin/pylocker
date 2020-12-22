from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, SecretStr

from .enum_models import TwoFactorDelivery, UsernameStatus
from ..schemas.utils import as_form


class UserBase(BaseModel):
    email: EmailStr
    fullName: Optional[str] = None
    mobilePhone: Optional[str] = None

    class Config:
        orm_mode = True


class UserInfo(UserBase):
    id: str
    active: bool
    passwordLastUpdateInstant: datetime
    usernameStatus: UsernameStatus
    twoFactorDelivery: TwoFactorDelivery
    verified: bool
    tenantId: str
    birthDate: Optional[date]
    passwordChangeRequired: bool
    insertInstant: int
    twoFactorEnabled: bool


# user sign up models
@as_form
class UserSignUp(UserBase):
    password1: SecretStr
    password2: SecretStr
    imageUrl: Optional[str] = None
    birthDate: Optional[date] = None
    twoFactorEnabled: bool = False
    skipVerification: bool = False


class AppRegistrationForm(BaseModel):
    applicationId: str
    roles: List[str]

    class Config:
        orm_mode = True


class UserRegistrationForm(UserBase):
    password: str
    birthDate: Optional[str] = None


class RegistrationRequest(BaseModel):
    registration: AppRegistrationForm
    user: UserRegistrationForm
    sendSetPasswordEmail: bool = False
    skipVerification: bool = False

    class Config:
        orm_mode = True
