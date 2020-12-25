from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .error_types import BasicError


async def basic_error_handler(
        request: Request, exception: BasicError
) -> Response:
    # TODO: logging with inclusion of request data
    return JSONResponse(
        status_code=exception.error_code,
        content=exception.error_message,
        media_type=exception.mimetype
    )


async def validation_error_handler(
        request: Request, exception: ValidationError
) -> Response:
    return JSONResponse(
        status_code=400,
        content=exception.errors()
    )
