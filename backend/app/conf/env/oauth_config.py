from pydantic_settings import BaseSettings


class OAuth2Settings(BaseSettings):
    """
    OAuth2 configuration settings for Gmail SSO
    """
    # Google OAuth2 settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Session settings
    SESSION_SECRET_KEY: str = "your-session-secret-key-change-in-production"
    
    class Config:
        env_prefix = "OAUTH2_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


