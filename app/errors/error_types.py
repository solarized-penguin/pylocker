from abc import ABC
from typing import Union, Dict, Any


def _parse_error_message(error_message: Union[str, Dict[str, Any]]) -> str:
    if isinstance(error_message, str):
        return error_message
    result = '\n'.join(
        [f'{key}: {value}' for key, value in error_message.items()]
    )
    return f"<{result}>"


class BasicError(ABC, Exception):
    def __init__(
            self, error_code: int, error_message: Union[str, Dict[str, Any]],
            mimetype: str = 'application/json'
    ):
        self.error_code: int = error_code
        self.error_message: Union[str, Dict[str, Any]] = error_message
        self.mimetype: str = mimetype

    def __repr__(self) -> str:
        _repr = dict(
            error_code=self.error_code,
            error_message=self.error_message,
            mimetype=self.mimetype
        )
        return str(_repr)

    def __str__(self) -> str:
        error_name = self.__class__.__name__

        return f'{error_name} | {self.error_code}\n{self.error_message}'


class UserSignUpError(BasicError):
    def __init__(self, error_message: Union[str, Dict[str, Any]]) -> None:
        super(UserSignUpError, self).__init__(error_code=400, error_message=error_message)


class UserSignInError(BasicError):
    def __init__(self, error_message: Union[str, Dict[str, Any]]) -> None:
        super(UserSignInError, self).__init__(error_code=401, error_message=error_message)


class UserInfoNotFoundError(BasicError):
    def __init__(self, error_code: int, error_message: Union[str, Dict[str, Any]]) -> None:
        super(UserInfoNotFoundError, self).__init__(
            error_code=error_code, error_message=error_message
        )
