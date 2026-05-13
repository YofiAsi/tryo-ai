from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LiteLLM proxy configuration. All LLM calls route through the proxy."""

    BASE_URL: str = "http://tyro-litellm:4000"
    MASTER_KEY: str = ""
    DEFAULT_CHAT_MODEL: str = "gpt-4o"
    DEFAULT_ANALYZER_MODEL: str = "gpt-4o-mini"

    class Config:
        env_prefix = "LITELLM_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
