# Database Configuration
import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

from app.entity.batch_entity import Batch
from app.entity.batch_task_entity import BatchTask
from app.entity.openai_client_entity import OpenAiClient

log = logging.getLogger(__name__)
client = None
db = None


class DatabaseSettings(BaseSettings):
    """
    Database settings

    Attributes:
    -----------
    MONGODB_URI: str
        MongoDB URI to connect to the database
    DATABASE_NAME: str
        Database name to connect to in MongoDB
    """

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
    """
    Load database settings from the environment variables
    """
    log.info("Loading database settings")
    mongodb_uri: str = ""
    db_settings = DatabaseSettings()
    log.debug(f"DatabaseSettings().MONGODB_URI: {db_settings.MONGODB_URI}")
    if db_settings.MONGODB_URI:
        mongodb_uri = db_settings.MONGODB_URI
    else:
        mongodb_uri = f"mongodb://{db_settings.HOST}:{db_settings.PORT}"
        if db_settings.USERNAME and db_settings.PASSWORD:
            mongodb_uri = f"mongodb://{db_settings.USERNAME}:{db_settings.PASSWORD}@{db_settings.HOST}:{db_settings.PORT}"

    log.debug(f"Database name: {db_settings.DATABASE_NAME}")
    log.debug(f"mongodb_uri: {mongodb_uri}")
    global client, db
    client = AsyncIOMotorClient(mongodb_uri)
    if not client:
        raise ValueError("Failed to connect to database")

    db = client[db_settings.DATABASE_NAME]

    await init_beanie(database=db, document_models=[Batch, BatchTask, OpenAiClient])


async def close_db_connection() -> None:
    """
    Close database connection
    """
    global client
    if client:
        client.close()
        log.info("Database connection closed")
