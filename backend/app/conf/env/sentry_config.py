import logging
from pydantic_settings import BaseSettings
from typing import Optional


class SentrySettings(BaseSettings):
    """
    Sentry settings for error monitoring and performance tracking
    
    Attributes:
    -----------
    SENTRY_DSN: Optional[str]
        Sentry DSN (Data Source Name) for project identification
    SENTRY_ENVIRONMENT: str
        Environment name (development, staging, production)
    SENTRY_TRACES_SAMPLE_RATE: float
        Percentage of transactions to sample for performance monitoring (0.0 to 1.0)
    SENTRY_PROFILES_SAMPLE_RATE: float
        Percentage of profiles to sample for performance profiling (0.0 to 1.0)
    SENTRY_ENABLE: bool
        Whether to enable Sentry integration
    """
    
    DSN: Optional[str] = None
    ENVIRONMENT: str = "development"
    TRACES_SAMPLE_RATE: float = 0.1
    PROFILES_SAMPLE_RATE: float = 0.1
    ENABLE: bool = False
    
    class Config:
        env_prefix = "SENTRY_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


sentry_settings = SentrySettings()


async def init_sentry() -> None:
    """
    Initialize Sentry SDK with the configured settings
    
    This function should be called during application startup to configure
    Sentry for error monitoring and performance tracking.
    """
    if not sentry_settings.ENABLE:
        logging.info("Sentry is disabled")
        return
    
    if not sentry_settings.DSN:
        logging.warning("Sentry is enabled but no DSN provided")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=sentry_settings.DSN,
            environment=sentry_settings.ENVIRONMENT,
            traces_sample_rate=sentry_settings.TRACES_SAMPLE_RATE,
            profiles_sample_rate=sentry_settings.PROFILES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            # Set a uniform sample rate for all transactions
            traces_sampler=lambda sampling_context: sentry_settings.TRACES_SAMPLE_RATE,
        )
        
        logging.info(f"Sentry initialized successfully for environment: {sentry_settings.ENVIRONMENT}")
        
    except ImportError:
        logging.error("sentry-sdk not installed. Sentry integration will be disabled.")
    except Exception as e:
        logging.error(f"Failed to initialize Sentry: {e}")


def is_sentry_enabled() -> bool:
    """
    Check if Sentry is currently enabled and configured
    
    Returns:
        True if Sentry is enabled and DSN is provided, False otherwise
    """
    return sentry_settings.ENABLE and sentry_settings.DSN is not None
