from functools import lru_cache
from typing import List

from pydantic import BaseSettings, PostgresDsn


def _comma_separated_env_str_to_list(env_str: str) -> List[str]:
    return [value.strip() for value in env_str.split(',') if value]


class Settings(BaseSettings):
    """
    | Settings model for entire application.
    | Values are read from environment.
    Available settings:
        1. General environment:
            * APP_ENV - specifies environment in which application will be run
            * PYTHONPATH - absolute path to database metadata files (**/app/core/database_models.py**)
            * PYTHONUNBUFFERED - disable buffering to get errors printed to console quicker, True by default.
        2. General API:
            * api_title - name of the app
            * api_description - apps description, shows under title in swagger
            * api_version - current app version
            * api_swagger_url - swagger documentation location: **<api address>/api_swagger_url**
            * api_redoc_url - redoc documentation location: **<api address>/api_redoc_url**
        3. Connections (database dsn, redis, itp...):
            * postgres_dsn - postgresql api database url
    """

    # General
    APP_ENV: str
    PYTHONPATH: str
    PYTHONUNBUFFERED: bool = True

    # API
    api_title: str
    api_description: str
    api_version: str
    api_swagger_url: str
    api_redoc_url: str

    # connections
    postgres_dsn: PostgresDsn

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Loads settings
    :rtype: Settings
    """
    return Settings()
