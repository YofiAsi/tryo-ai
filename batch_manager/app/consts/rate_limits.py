"""
OpenAI Batch API Rate Limits and Constraints

Official limits for OpenAI Batch API processing.
These limits are separate from standard per-model rate limits.
"""

from typing import Dict

from app.consts.ai_models import AIModel

MAX_REQUESTS_PER_BATCH = 50_000
"""Maximum number of requests allowed in a single batch"""

MAX_BATCH_INPUT_FILE_SIZE_MB = 200
"""Maximum size of input file for a batch in megabytes"""

MAX_BATCH_INPUT_FILE_SIZE_BYTES = MAX_BATCH_INPUT_FILE_SIZE_MB * 1024 * 1024
"""Maximum size of input file for a batch in bytes"""

MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD: Dict[AIModel, int] = {
    # GPT-5 Series
    AIModel.GPT_5: 200_000_000,
    AIModel.GPT_5_MINI: 1_000_000_000,
    AIModel.GPT_5_NANO: 1_000_000_000,
    
    # GPT-4.1 Series
    AIModel.GPT_4_1: 200_000_000,
    AIModel.GPT_4_1_MINI: 1_000_000_000,
    AIModel.GPT_4_1_NANO: 1_000_000_000,
    
    # O Series
    AIModel.O3: 200_000_000,
    AIModel.O4_MINI: 1_000_000_000,

    # Text Embedding 3
    AIModel.TEXT_EMBEDDING_3_LARGE: 500_000_000,
    AIModel.TEXT_EMBEDDING_3_SMALL: 500_000_000,
}