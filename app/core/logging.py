import sys

from loguru import logger

from .settings import Settings


def configure_logging() -> None:
    _settings: Settings = Settings.get()

    logger.remove()
    logger.add(
        sys.stderr,
        format=_settings.log_format,
        level=_settings.log_level,
        backtrace=True,
        diagnose=True,
        catch=True,
        colorize=True
    )
    logger.add(
        _settings.log_file_path,
        format=_settings.log_format,
        level=_settings.log_level,
        backtrace=True,
        diagnose=True,
        catch=True,
        rotation="00:00"
    )
