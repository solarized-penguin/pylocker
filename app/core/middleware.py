from time import time
from typing import Callable, Any

from fastapi import FastAPI, Response, Request
from loguru import logger


def register_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def log_requests(
            request: Request, call_next: Callable[..., Any]
    ) -> Response:
        logger.info(f'Request starts, path: {request.url}, method: {request.method}')

        start_time = time()
        response: Response = await call_next(request)
        request_execution_time = time() - start_time

        logger.info(f'Request execution time: {request_execution_time}')
        return response
