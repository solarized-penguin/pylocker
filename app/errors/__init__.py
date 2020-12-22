from fastapi import FastAPI

from .error_handlers import basic_error_handler
from .error_types import UserSignUpError, UserSignInError


def register_error_handlers(app: FastAPI) -> None:
    """
    Registers all errors with custom errors handlers.
    :param app: FastAPI app instance
    """
    app.add_exception_handler(UserSignUpError, basic_error_handler)
    app.add_exception_handler(UserSignInError, basic_error_handler)
