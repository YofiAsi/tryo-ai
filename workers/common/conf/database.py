# Database Configuration
import logging
from typing import Any

from beanie import init_beanie
from pydantic_settings import BaseSettings
from pymongo import AsyncMongoClient

from common.entity import get_db_entities

log = logging.getLogger(__name__)
client: AsyncMongoClient[Any] | None = None
db = None


class DatabaseSettings(BaseSettings):
    MONGODB_URI: str | None = None
    DATABASE_NAME: str = "tyro-db"
    HOST: str = "localhost"
    PORT: int = 27017
    USERNAME: str | None = None
    PASSWORD: str | None = None

    class Config:
        env_prefix = "DB_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


async def init_db() -> None:
    """Initialize the database connection and Beanie ODM."""
    log.info("Loading database settings")
    db_settings = DatabaseSettings()

    if db_settings.MONGODB_URI:
        mongodb_uri = db_settings.MONGODB_URI
    else:
        auth = ""
        if db_settings.USERNAME and db_settings.PASSWORD:
            auth = f"{db_settings.USERNAME}:{db_settings.PASSWORD}@"
        mongodb_uri = f"mongodb://{auth}{db_settings.HOST}:{db_settings.PORT}"

    log.debug(f"Database name: {db_settings.DATABASE_NAME}")
    log.debug(f"MongoDB URI: {mongodb_uri}")

    global client, db
    client = AsyncMongoClient(mongodb_uri)
    await client.aconnect()
    db = client[db_settings.DATABASE_NAME]

    # Get all database entities from the entity module
    db_entities = get_db_entities()
    log.info(f"Initializing Beanie with entities: {[entity.__name__ for entity in db_entities]}")
    
    await init_beanie(database=db, document_models=db_entities)
    log.info("Database initialization completed successfully")


async def close_db_connection() -> None:
    """Close the database connection."""
    global client
    if client:
        await client.close()
        log.info("Database connection closed")
