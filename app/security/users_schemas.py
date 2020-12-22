from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, SecretStr

from ..schemas.utils import as_form


class UsernameStatus(str, Enum):
    ACTIVE = 'ACTIVE',
    """Username is active"""

    PENDING = 'PENDING',
    """Username is pending approval/moderation"""

    REJECTED = 'REJECTED'
    """Username was rejected during moderation"""


class TwoFactorDelivery(str, Enum):
    NONE = 'None',
    TextMessage = 'TextMessage'


class UserBase(BaseModel):
    email: EmailStr
    fullName: Optional[str] = None
    mobilePhone: Optional[str] = None
    birthDate: Optional[date] = None

    class Config:
        orm_mode = True


class UserRead(UserBase):
    id: str
    active: bool
    passwordLastUpdateInstant: datetime
    usernameStatus: UsernameStatus
    twoFactorDelivery: TwoFactorDelivery
    timezone: str
    preferredLanguages: List[str]
    verified: bool
    tenantId: str
    passwordChangeRequired: bool
    insertInstant: int
    twoFactorEnabled: bool


@as_form
class UserSignUp(UserBase):
    password1: SecretStr
    password2: SecretStr
    imageUrl: Optional[str] = None
    twoFactorEnabled: bool = False
    skipVerification: bool = False


class UserWrite(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class Registration(BaseModel):
    applicationId: str
    roles: List[str]

    class Config:
        orm_mode = True


class UserRegistrationRequest(BaseModel):
    registrations: List[Registration]
    user: UserWrite
    sendSetPasswordEmail: bool = False
    skipVerification: bool = False

    class Config:
        orm_mode = True
