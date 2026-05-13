"""LLM model factory.

Every agent talks to the LiteLLM proxy via an OpenAI-compatible endpoint, so we
only need one Model class regardless of which upstream provider serves the
request. The frontend selects the upstream model by name; LiteLLM routes it.
"""

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from app.conf.env.llm_config import LLMSettings


def build_model(
    model_name: str,
    settings: LLMSettings,
    *,
    temperature: float = 0.0,
    max_tokens: int = 16384,
) -> Model:
    return OpenAIModel(
        model_name,
        settings=ModelSettings(temperature=temperature, max_tokens=max_tokens),
        provider=OpenAIProvider(
            base_url=f"{settings.BASE_URL}/v1",
            api_key=settings.MASTER_KEY or "not-needed",
        ),
    )
