from typing import AsyncGenerator, Generator

import pytest
from aredis import StrictRedis
from assertpy import add_extension
from databases import Database
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core import Settings
from app.core.database_schema import db_schema
from .utils import config_queries
from .utils.assert_extensions import is_successful_status_code, is_validation_message_correct

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
