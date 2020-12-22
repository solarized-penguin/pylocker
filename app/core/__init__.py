from typing import Callable

from databases import Database
from fastapi import FastAPI, Response, Request, Depends

from .settings import get_settings, Settings
from ..errors import register_error_handlers
from ..routers import register_routers


def create_app() -> FastAPI:
    """
    | Factory methods that returns independent instances of this application.
    :return: Instance of the application
    :rtype: FastAPI
    """
    # initialize settings
    _settings: Settings = get_settings()

    # create base api
    app: FastAPI = FastAPI(
        title=_settings.api_title,
        description=_settings.api_description,
        version=_settings.api_version,
        docs_url=_settings.api_swagger_url,
        redoc_url=_settings.api_redoc_url
    )

    # register routers
    register_routers(app)

    # register error handlers
    register_error_handlers(app)

    # register database provider
    db_pool: Database = Database(
        url=_settings.postgres_dsn
    )

    # register middleware
    @app.middleware('http')
    async def enrich_request_with_database_connection_pool(request: Request, call_next: Callable):
        request.state.db = db_pool
        response: Response = await call_next(request)
        return response

    # start/stop db pool
    @app.on_event('startup')
    async def startup():
        await db_pool.connect()

    @app.on_event('shutdown')
    async def shutdown():
        await db_pool.disconnect()

    return app


def get_db(request: Depends(Request)) -> Database:
    return request.state.db
