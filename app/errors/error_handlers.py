from asyncpg import PostgresError
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError

from .error_types import BasicError


async def basic_error_handler(
        request: Request, exception: BasicError
) -> Response:
    logger.error(f'{request.method} | {request.url} | {exception}')
    return JSONResponse(
        status_code=exception.error_code,
        content=exception.error_message,
        media_type=exception.mimetype
    )


async def validation_error_handler(
        request: Request, exception: ValidationError
) -> Response:
    logger.error(f'{request.method} | {request.url} | 400 | {exception.json()}')
    return JSONResponse(
        status_code=400,
        content=exception.errors()
    )


async def postgres_error_handler(
        request: Request, exception: PostgresError
) -> Response:
    logger.error(f'{request.method} | {request.url} | 400 | {exception.as_dict()}')
    return JSONResponse(
        status_code=400,
        content=exception.as_dict()
    )


async def http_error_handler(
        request: Request, exception: HTTPException
) -> Response:
    logger.error(f'{request.method} | {request.url} | {exception.status_code} | '
                 f'{exception.detail}')
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.detail
    )
