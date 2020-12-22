import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, PostgresDsn, SecretStr

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
    | Settings model for entire application.
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
            * postgres_dsn - postgresql api database url
        4. Security (OAuth2, OpenId Connect):
            * api_key - api key
            * app_id - application id
            * auth_provider_url - base address of identity provider
            * token_url - url that should be used to obtain access token
        5. Scopes/Roles:
            * standard_user_roles - roles assigned by default to standard user account
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

    # security
    api_key: SecretStr
    app_id: SecretStr
    client_id: SecretStr
    client_secret: SecretStr

    auth_provider_url: str
    token_url: str

    # roles\scopes
    standard_user_roles_list: str

    @property
    def standard_user_roles(self) -> List[str]:
        return _comma_separated_env_str_to_list(self.standard_user_roles_list)

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Loads settings and
    sets up environment
    :rtype: Settings
    """
    _set_up_environment()

    return Settings()
