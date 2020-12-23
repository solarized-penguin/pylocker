import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core import Settings, get_settings
from .utils import queries

base_db_url: str = 'postgresql://postgres:postgres@0.0.0.0:5433/postgres'
test_db_name: str = 'pylocker_test_db'

settings: Settings = get_settings()


@pytest.fixture(scope='session')
def engine() -> Engine:
    return create_engine(base_db_url)


@pytest.fixture(scope='session', autouse=True)
def setup_database(engine) -> None:
    drop_if_exists_query = queries \
        .drop_database_if_exists \
        .replace(':dbname', 'test_db_name')
    engine.execute(text(drop_if_exists_query))
