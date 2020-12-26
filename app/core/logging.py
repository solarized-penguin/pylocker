import sys

from loguru import logger

from .settings import get_settings, Settings


def configure_logging() -> None:
    _settings: Settings = get_settings()

    logger.add(
        sys.stderr,
        format=_settings.log_format,
        level=_settings.log_level,
        colorize=True
    )
    logger.add(
        _settings.log_file_path,
        rotation=_settings.log_file_rotation,
        format=_settings.log_format,
        level=_settings.log_level,
        backtrace=True,
        diagnose=True,
        catch=True
    )
