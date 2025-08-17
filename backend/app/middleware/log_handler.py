import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from app.conf.app_settings import log_settings, app_settings




def get_console_handler():
    console_handler = logging.StreamHandler()
    # console_handler.setLevel(log_settings.LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(log_settings.LOG_FORMAT))
    return console_handler


def get_file_time_rotation_handler():
    time_rotation_handler = TimedRotatingFileHandler(
        filename=log_settings.LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=log_settings.LOG_MAX_DAYS,
        encoding="utf-8",
        delay=False,
        utc=True,
        atTime=None,
        errors=None)
    # time_rotation_handler.setLevel(log_settings.LOG_LEVEL)
    # time_rotation_handler.setFormatter(logging.Formatter(log_settings.LOG_FORMAT))
    return time_rotation_handler


def get_file_size_rotation_handler():
    size_rotation_handler = RotatingFileHandler(
        filename=log_settings.LOG_FILE,
        mode="a",
        maxBytes=log_settings.LOG_MAX_SIZE,
        backupCount=log_settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
        delay=False,
        errors=None)
    # size_rotation_handler.setLevel(log_settings.LOG_LEVEL)
    # size_rotation_handler.setFormatter(logging.Formatter(log_settings.LOG_FORMAT))
    return size_rotation_handler


def configure_handler():
    _handlers = []

    if "file" in log_settings.LOG_HANDLER:
        _handlers.append(get_file_time_rotation_handler())
        _handlers.append(get_file_size_rotation_handler())

    if "console" in log_settings.LOG_HANDLER or not _handlers:
        _handlers.append(get_console_handler())

    return _handlers



def init_log():
    logging.basicConfig(
        level=log_settings.LOG_LEVEL,
        format=log_settings.LOG_FORMAT,
        handlers=configure_handler()
    )

    logging.getLogger("asyncio").setLevel(logging.WARN)
    logging.getLogger("pymongo").setLevel(logging.WARN)
    logging.getLogger("uvicorn").setLevel(logging.WARN)
    logging.getLogger("pydantic").setLevel(logging.WARN)
    logging.getLogger("fastapi").setLevel(logging.WARN)
    logging.getLogger("beanie").setLevel(logging.WARN)
    logging.getLogger("urllib3").setLevel(logging.WARN)
    logging.getLogger("passlib").setLevel(logging.WARN)
    logging.getLogger("starlette").setLevel(logging.WARN)
    logging.getLogger("bitsandbytes").setLevel(logging.WARN)
    logging.getLogger("sentence_transformers").setLevel(logging.WARN)
    log = logging.getLogger(__name__)
    log.info(f"{app_settings.APP_NAME} Application started")
    return log