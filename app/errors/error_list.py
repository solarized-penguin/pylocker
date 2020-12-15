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
        self._error_code: int = error_code
        self._error_message: Union[str, Dict[str, Any]] = error_message
        self._mimetype: str = mimetype

    def __repr__(self):
        _repr = dict(
            error_code=self._error_code,
            error_message=self._error_message,
            mimetype=self._mimetype
        )
        return str(_repr)

    def __str__(self):
        return f'error_code: {self._error_code}\n' \
               f'error_message: {_parse_error_message(self._error_message)}\n' \
               f'mimetype: {self._mimetype}'
