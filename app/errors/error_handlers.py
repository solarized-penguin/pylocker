from fastapi import Request, Response

from .error_types import BasicError


async def basic_error_handler(
        request: Request, exception: BasicError
) -> Response:
    # TODO: logging with inclusion of request data
    return Response(
        status_code=exception.error_code,
        content=exception.error_message,
        media_type=exception.mimetype
    )
