from fastapi import FastAPI

from .error_handlers import basic_error_handler
from .error_types import UserRegistrationError


def register_error_handlers(app: FastAPI) -> None:
    """
    Registers all errors with custom errors handlers.
    :param app: FastAPI app instance
    """
    app.add_exception_handler(UserRegistrationError, basic_error_handler)
