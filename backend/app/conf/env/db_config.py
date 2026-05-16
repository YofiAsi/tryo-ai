# Database Configuration
import logging
from typing import Any, Optional

from beanie import init_beanie
from pydantic_settings import BaseSettings
from pymongo import AsyncMongoClient

from app import entity

log = logging.getLogger(__name__)

# Keep global handles if you need them elsewhere
client: Optional[AsyncMongoClient[Any]] = None
db = None


class DatabaseSettings(BaseSettings):
    """
    Database settings
    """
    MONGODB_URI: str | None = None
    DATABASE_NAME: str = "app"
    HOST: str = "localhost"
    PORT: int = 27017
    USERNAME: str | None = None
    PASSWORD: str | None = None
    LOG_COLLECTION: str = "app_log"

    class Config:
        env_prefix = "DB_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


async def init_db() -> None:
    """
    Initialize the database + Beanie with PyMongo's async client
    """
    log.info("Loading database settings")
    settings = DatabaseSettings()

    # Build URI once
    if settings.MONGODB_URI:
        mongodb_uri = settings.MONGODB_URI
    else:
        auth = ""
        if settings.USERNAME and settings.PASSWORD:
            auth = f"{settings.USERNAME}:{settings.PASSWORD}@"
        mongodb_uri = f"mongodb://{auth}{settings.HOST}:{settings.PORT}"

    log.debug(f"Database name: {settings.DATABASE_NAME}")
    log.debug(f"mongodb_uri: {mongodb_uri}")

    global client, db
    client = AsyncMongoClient[Any](mongodb_uri)
    db = client[settings.DATABASE_NAME]

    # Optional: verify connectivity early (uncomment if you want a startup check)
    # await db.command("ping")

    # Register your Beanie models
    await init_beanie(
        database=db,
        document_models=[
            entity.User,
            entity.JobPosition,
            entity.Candidate,
            entity.Task,
        ],
    )


async def close_db_connection() -> None:
    """
    Close database connection
    """
    global client
    if client:
        # PyMongo async close() returns an awaitable; if your version changes,
        # this pattern safely handles either case.
        res = client.close()
        try:
            # If close() is awaitable, await it
            import inspect
            if inspect.isawaitable(res):
                await res
        except Exception:
            # If not awaitable, it's already closed synchronously
            pass
        log.info("Database connection closed")
