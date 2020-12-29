from typing import Callable, Any

from aredis import StrictRedis
from databases import Database
from fastapi import FastAPI, Response, Request

from .logging import configure_logging
from .settings import Settings
from ..errors import register_error_handlers
from ..routers import register_routers


def create_app() -> FastAPI:
    """
    | Factory method that returns independent instance of this application.
    :return: Instance of the application
    :rtype: FastAPI
    """
    # initialize settings
    _settings: Settings = Settings.get()

    # create api instance
    app: FastAPI = FastAPI(
        title=_settings.api_title,
        description=_settings.api_description,
        version=_settings.api_version,
        docs_url=_settings.api_swagger_url,
        redoc_url=_settings.api_redoc_url
    )

    # configure logging
    configure_logging()

    # register routers
    register_routers(app)

    # register error handlers
    register_error_handlers(app)

    # register database provider
    db_pool: Database = Database(
        url=_settings.postgres_dsn
    )

    # register redis
    redis: StrictRedis = StrictRedis.from_url(_settings.redis_dsn)

    # register database middleware
    @app.middleware('http')
    async def enrich_request_with_database_connection_pool_and_redis(
            request: Request, call_next: Callable[..., Any]
    ) -> Response:
        """
        Enriches every request with database and redis instance
        so they can be accessed from routers.
        :param request: current request
        :param call_next: request/response interface
        :return: response
        :rtype: Response
        """
        request.state.db = db_pool
        request.state.redis = redis
        response: Response = await call_next(request)
        return response

    # start/stop db pool
    @app.on_event('startup')
    async def startup() -> None:
        """
        Starts database connection pool
        with application start.
        :return:
        """
        await db_pool.connect()

    @app.on_event('shutdown')
    async def shutdown() -> None:
        """
        Disconnects database connection pool
        before application shuts down.
        :return:
        """
        await db_pool.disconnect()

    return app


def get_db(request: Request) -> Database:
    """
    Factory method returns database pool object
    extracted from request.
    :param request: current request
    :return: database pool
    :rtype: Database
    """
    return request.state.db


def get_redis(request: Request) -> StrictRedis:
    """
    Factory method returns redis connection
    extracted from request.
    :param request: current request
    :return: redis connection
    :rtype: StrictRedis
    """
    return request.state.redis
