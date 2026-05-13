# Database Configuration
import logging
from typing import Any

from app.entity.batch_entity import Batch
from app.entity.batch_task_entity import BatchTask
from app.entity.openai_client_entity import OpenAiClient
from beanie import init_beanie
from pydantic_settings import BaseSettings
from pymongo import AsyncMongoClient

log = logging.getLogger(__name__)
client: AsyncMongoClient[Any] | None = None
db = None

class DatabaseSettings(BaseSettings):
    MONGODB_URI: str | None = None
    DATABASE_NAME: str = "tyro-batch-manager"
    HOST: str = "localhost"
    PORT: int = 27017
    USERNAME: str | None = None
    PASSWORD: str | None = None
    LOG_COLLECTION: str = "batch-manager-log"

    class Config:
        env_prefix = "DB_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

async def init_db() -> None:
    log.info("Loading database settings")
    db_settings = DatabaseSettings()

    if db_settings.MONGODB_URI:
        mongodb_uri = db_settings.MONGODB_URI
    else:
        auth = ""
        if db_settings.USERNAME and db_settings.PASSWORD:
            auth = f"{db_settings.USERNAME}:{db_settings.PASSWORD}@"
        mongodb_uri = f"mongodb://{auth}{db_settings.HOST}:{db_settings.PORT}"

    global client, db
    client = AsyncMongoClient(mongodb_uri)
    await client.aconnect()                              # optional but useful “eager” connect
    db = client[db_settings.DATABASE_NAME]               # AsyncDatabase

    await init_beanie(database=db, document_models=[Batch, BatchTask, OpenAiClient])

async def close_db_connection() -> None:
    global client
    if client:
        await client.close()                             # close() is async in the async API
        log.info("Database connection closed")
