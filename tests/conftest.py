from typing import Any, AsyncGenerator

import pytest
from databases import Database
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core import Settings, get_settings
from .utils import queries

base_db_url: str = 'postgresql://postgres:postgres@0.0.0.0:5433/postgres'
test_db_name: str = 'pylocker_test_db'

settings: Settings = get_settings()


@pytest.fixture(scope='session', autouse=True)
def create_test_database() -> None:
    engine: Engine = create_engine(base_db_url)
    with engine.connect() as conn:
        conn.connection.set_isolation_level(
            ISOLATION_LEVEL_AUTOCOMMIT
        )
        conn.execute(
            queries.drop_database_if_exists \
                .replace(':dbname', test_db_name)
        )
        conn.execute(
            queries.create_database \
                .replace(':dbname', test_db_name)
        )
        yield
        conn.execute(
            queries.drop_database_if_exists \
                .replace(':dbname', test_db_name)
        )


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def db() -> AsyncGenerator[Any, Database]:
    db: Database = Database(settings.postgres_dsn)
    await db.connect()
    yield db
    await db.disconnect()
