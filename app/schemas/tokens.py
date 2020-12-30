from enum import Enum

from pydantic import BaseModel


class TokenType(str, Enum):
    Bearer = 'Bearer'


class Token(BaseModel):
    access_token: str
    token_type: TokenType = TokenType.Bearer

    class Config:
        orm_mode = True
