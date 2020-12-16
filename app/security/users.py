from datetime import datetime
from enum import Enum
from typing import Optional, List
from fastapi import Form
from pydantic import BaseModel, EmailStr, SecretStr


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
    birthDate: Optional[datetime] = None

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


class UserWrite(UserBase):
    password1: SecretStr
    password2: SecretStr
    imageUrl: Optional[str] = None
    twoFactorEnabled: bool = False
    skipVerification: bool = False

    @classmethod
    def as_form(
            cls,
            email: Form = Form(..., description='used as username as well'),
            fullName: Form = Form(None, description='first and last name'),
            mobilePhone: Form = Form(None, description='phone number'),
            birthDate: Form = Form(None, description='day of birth'),
            password1: Form = Form(..., description='account password'),
            password2: Form = Form(..., description='password repeat'),
            imageUrl: Form = Form(None, description='account avatar/picture url'),
            twoFactorEnabled: Form = Form(False, description='is 2FA enabled for this account?'),
            skipVerification: Form = Form(False, description='skip verification during user creation process?')
    ) -> Form:
        cls(
            email=email, fullName=fullName, mobilePhone=mobilePhone,
            birthDate=birthDate, password1=password1, password2=password2,
            imageUrl=imageUrl, twoFactorEnabled=twoFactorEnabled,
            skipVerification=skipVerification
        )


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
