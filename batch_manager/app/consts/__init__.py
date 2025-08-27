"""Constants package for the tyro-batch-manager application."""

from app.consts.ai_models import AIModel, EnumHasValue
from app.consts.rate_limits import (
    MAX_BATCH_INPUT_FILE_SIZE_BYTES,
    MAX_BATCH_INPUT_FILE_SIZE_MB,
    MAX_REQUESTS_PER_BATCH,
    MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD,
)

__all__ = [
    # AI Models
    "AIModel",
    "EnumHasValue",
    # Rate Limits
    "MAX_BATCH_INPUT_FILE_SIZE_BYTES",
    "MAX_BATCH_INPUT_FILE_SIZE_MB", 
    "MAX_REQUESTS_PER_BATCH",
    "MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD",
]
