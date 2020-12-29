from __future__ import annotations

import re
from datetime import datetime, date
from typing import Optional, List, Union, Dict, Any

from fastapi import Form
from pydantic import BaseModel, EmailStr, SecretStr, validator, HttpUrl

from .enum_models import TwoFactorDelivery, UsernameStatus
from .user_validations import UserValidationRules


class UserBase(BaseModel):
    email: EmailStr
    fullName: Optional[str] = None
    mobilePhone: Optional[str] = None

    @validator('fullName')
    def must_contain_space_between_names(cls, v: Union[str, None]) -> Union[str, None]:
        if isinstance(v, str) and ' ' not in v.strip():
            raise ValueError(UserValidationRules.full_name_error_message)
        return v

    @validator('mobilePhone')
    def mobile_must_be_correct_format(cls, v: Union[str, None]) -> Union[str, None]:
        if isinstance(v, str) and not re.match(UserValidationRules.mobile_regex, v):
            raise ValueError(UserValidationRules.mobile_error_message)
        return v

    class Config:
        orm_mode = True


class UserInfo(UserBase):
    id: str
    imageUrl: Optional[HttpUrl]
    birthDate: Optional[date]
    active: bool
    passwordLastUpdateInstant: datetime
    usernameStatus: UsernameStatus
    twoFactorDelivery: TwoFactorDelivery
    verified: bool
    tenantId: str
    passwordChangeRequired: bool
    insertInstant: int


# user sign up models
class UserSignUp(UserBase):
    password1: SecretStr
    password2: SecretStr
    imageUrl: Optional[HttpUrl] = None
    birthDate: Optional[date] = None

    @validator('password1')
    def password_complexity_rules(cls, v: SecretStr) -> SecretStr:
        if not re.match(UserValidationRules.password_regex, v.get_secret_value()):
            raise ValueError(UserValidationRules.password_error_message)
        return v

    @validator('password2')
    def passwords_match(
            cls, v: SecretStr, values: Dict[str, Any], **kwargs: Any
    ) -> SecretStr:
        if 'password1' in values and not \
                v.get_secret_value() == \
                values['password1'].get_secret_value():
            raise ValueError(UserValidationRules.passwords_not_match_error_message)
        return v

    @classmethod
    def as_form(
            cls,
            email: EmailStr = Form(..., description='User email, used as username across application.'),
            fullName: Optional[str] = Form(None, description='At least first and last name.'),
            mobilePhone: Optional[str] = Form(None, description='Phone number.'),
            password1: SecretStr = Form(..., description='Account password.'),
            password2: SecretStr = Form(..., description='Password repeat.'),
            imageUrl: Optional[HttpUrl] = Form(None, description='Url to profile image.'),
            birthDate: Optional[date] = Form(None, description='Birth date in format: YYYY-mm-dd')
    ) -> UserSignUp:
        return cls(email=email, fullName=fullName, mobilePhone=mobilePhone, password1=password1,
                   password2=password2, imageUrl=imageUrl, birthDate=birthDate)


class AppRegistrationForm(BaseModel):
    applicationId: str
    roles: List[str]

    class Config:
        orm_mode = True


class UserRegistrationForm(UserBase):
    password: str
    birthDate: Optional[str] = None
    imageUrl: Optional[HttpUrl] = None


class RegistrationRequest(BaseModel):
    registration: AppRegistrationForm
    user: UserRegistrationForm
    sendSetPasswordEmail: bool = False
    skipVerification: bool = False

    class Config:
        orm_mode = True
