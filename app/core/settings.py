from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, PostgresDsn, SecretStr, RedisDsn

DB_SCHEMA = './database_schema.py'


def _comma_separated_env_str_to_list(env_str: str) -> List[str]:
    return [value.strip() for value in env_str.split(',') if value]


def _set_up_environment() -> None:
    """
    Sets correct PYTHONPATH and PYTHONUNBUFFERED
    environmental variables
    """
    full_path = os.path.abspath(DB_SCHEMA)
    pythonpath = os.environ['PYTHONPATH']

    os.environ['PYTHONPATH'] = f'{pythonpath}:{full_path}'
    os.environ['PYTHONUNBUFFERED'] = str(True)


class Settings(BaseSettings):
    """
    | Settings for entire application.
    | Values are read from environment.
    Available settings:
        1. General environment info:
            * app_env - specifies environment in which application will be run
        2. General API:
            * api_title - name of the app
            * api_description - apps description, shows under title in swagger
            * api_version - current app version
            * api_swagger_url - swagger documentation location: **<api address>/api_swagger_url**
            * api_redoc_url - redoc documentation location: **<api address>/api_redoc_url**
        3. Connections (database dsn, redis, itp...):
            * postgres_dsn - postgresql connection string
            * redis_host - address of redis host
            * redis_port - port on which redis is listening
            * redis_db - redis database to use
        4. Security (OAuth2, OpenId Connect):
            * api_key - api key
            * app_id - application id
            * auth_provider_url - base address of identity provider
            * token_url - url that should be used to obtain access token
        5. Scopes/Roles:
            * standard_user_roles - roles assigned by default to standard user account
        6. Logging:
            * log_format - log message formatting
            * log_level - minimal logging level
            * log_file_path - path to log file
        7. Files:
            * max_chunk_size - maximal size of a single chunk
    """

    # General environment info
    app_env: str

    # api
    api_title: str
    api_description: str
    api_version: str
    api_swagger_url: str
    api_redoc_url: str

    # connections
    postgres_dsn: PostgresDsn
    redis_dsn: RedisDsn

    # auth_client
    api_key: SecretStr
    app_id: SecretStr

    jwt_signing_key: SecretStr
    jwt_algorithms_list: str

    client_id: SecretStr
    client_secret: SecretStr
    auth_provider_url: str
    token_url: str

    # roles\scopes
    standard_user_roles_list: str

    # logging
    log_format: str
    log_level: str
    log_file_path: str

    # files
    location_url_bytes: int
    max_chunk_size: int

    @property
    def standard_user_roles(self) -> List[str]:
        return _comma_separated_env_str_to_list(self.standard_user_roles_list)

    @property
    def jwt_algorithms(self) -> List[str]:
        return _comma_separated_env_str_to_list(self.jwt_algorithms_list)

    class Config:
        case_sensitive = False

    @classmethod
    @lru_cache()
    def get(cls) -> Settings:
        """
        Loads settings and
        sets up environment
        :rtype: Settings
        """
        _set_up_environment()

        return Settings()
