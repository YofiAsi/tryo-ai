from pydantic_settings import BaseSettings
from app.conf.env.log_config import LoggingSettings
from app.conf.env.cors_config import CorsSettings
from app.conf.env.server_config import ServerSettings
from app.conf.env.db_config import DatabaseSettings
from app.conf.env.llm_config import LLMSettings


class ApplicationSettings(BaseSettings):
    """
    Application settings
    """
    APP_NAME: str = "PyFAPI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Python FastAPI mongodb app for Enterprise usage with best practices, tools, and more."
    APP_URL: str = "http://localhost:8000"
    APP_DEBUG: bool = True

    class Config:
        env_prefix = "APP_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


app_settings = ApplicationSettings()
log_settings = LoggingSettings()
cors_settings = CorsSettings()
server_settings = ServerSettings()
db_settings = DatabaseSettings()
llm_settings = LLMSettings()