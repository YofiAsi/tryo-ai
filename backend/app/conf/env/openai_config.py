from pydantic_settings import BaseSettings


class OpenAISettings(BaseSettings):
    """
    OpenAI configuration settings for AI agents
    """
    # OpenAI API settings
    API_KEY: str = ""
    
    class Config:
        env_prefix = "OPENAI_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
