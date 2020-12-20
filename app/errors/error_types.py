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
        return f'error_code: {self.error_code}\n' \
               f'error_message: {_parse_error_message(self.error_message)}\n' \
               f'mimetype: {self.mimetype}'


class UserRegistrationError(BasicError):
    def __init__(self, error_code: int, error_message: Union[str, Dict[str, Any]]) -> None:
        super().__init__(error_code=error_code, error_message=error_message)


class UserNotFoundError(BasicError):
    def __init__(self, error_message: Union[str, Dict[str, Any]]) -> None:
        super().__init__(error_code=401, error_message=error_message)
