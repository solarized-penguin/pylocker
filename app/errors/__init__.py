from asyncpg import UndefinedObjectError
from fastapi import FastAPI
from pydantic import ValidationError

from .error_handlers import basic_error_handler, validation_error_handler, postgres_error_handler
from .error_types import UserSignUpError, UserSignInError, UserInfoNotFoundError


def register_error_handlers(app: FastAPI) -> None:
    """
    Registers all errors with custom errors handlers.
    :param app: FastAPI app instance
    """
    app.add_exception_handler(UserSignUpError, basic_error_handler)
    app.add_exception_handler(UserSignInError, basic_error_handler)
    app.add_exception_handler(UserInfoNotFoundError, basic_error_handler)
    app.add_exception_handler(UndefinedObjectError, postgres_error_handler)

    app.add_exception_handler(ValidationError, validation_error_handler)
