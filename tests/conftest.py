from typing import AsyncGenerator, Generator

import pytest
from aredis import StrictRedis
from assertpy import add_extension
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from starlette.testclient import TestClient

from app import create_app
from app.auth_client import logged_user
from app.core import Settings, get_db, get_redis
from app.core.database_schema import db_schema
from .utils import config_queries
from .utils.assert_extensions import is_successful_status_code, is_validation_message_correct
from .utils.shared_test_utils import user_id_1

base_db_url: str = 'postgresql://postgres:postgres@0.0.0.0:5433/postgres'
test_db_name: str = 'pylocker_test_db'

settings: Settings = Settings.get()


@pytest.fixture(scope='session')
def assertion_extensions() -> None:
    add_extension(is_successful_status_code)
    add_extension(is_validation_message_correct)


@pytest.fixture(scope='session', autouse=True)
def create_test_database() -> Generator[None, None, None]:
    base_db_engine: Engine = create_engine(base_db_url)
    with base_db_engine.connect() as conn:
        conn.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        conn.execute(config_queries.drop_database_if_exists.replace('dbname', test_db_name))
        conn.execute(config_queries.create_database.replace('dbname', test_db_name))

        test_db_engine: Engine = create_engine(settings.postgres_dsn)
        db_schema.create_all(test_db_engine)
        test_db_engine.dispose()

        yield
        conn.execute(config_queries.drop_database_if_exists.replace('dbname', test_db_name))


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def redis() -> AsyncGenerator[StrictRedis, None]:
    redis: StrictRedis = StrictRedis.from_url(settings.redis_dsn)
    yield redis


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def db() -> AsyncGenerator[Database, None]:
    db: Database = Database(settings.postgres_dsn)
    await db.connect()
    yield db
    await db.disconnect()


@pytest.fixture(scope='function')
def client(db: Database) -> Generator[TestClient, None, None]:
    app: FastAPI = create_app()

    def _get_db() -> Database: return db

    app.dependency_overrides[get_db] = _get_db

    client: TestClient = TestClient(app)
    yield client


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def aclient(
        db: Database, redis: StrictRedis
) -> AsyncGenerator[AsyncClient, None]:
    app: FastAPI = create_app()

    def _get_db() -> Database: return db

    def _get_redis() -> StrictRedis: return redis

    def _logged_user() -> str: return user_id_1.email

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_redis] = _get_redis
    app.dependency_overrides[logged_user] = _logged_user

    aclient: AsyncClient = AsyncClient(app=app, base_url='http://testserver')
    yield aclient
    await aclient.aclose()
