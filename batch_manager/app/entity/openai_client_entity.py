from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from beanie import Document, Replace, Update, before_event
from pydantic import Field

from app.consts.ai_models import AIModel
from app.consts.rate_limits import MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD


@dataclass
class ClientResponse:
    client_name: str
    response: Any

class OpenAiClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class OpenAiClient(Document):
    name: str
    organization: Optional[str] = None
    project: Optional[str] = None
    status: OpenAiClientStatus = OpenAiClientStatus.ACTIVE
    model_usage: Dict[AIModel, int] = Field(default_factory=lambda: {model: 0 for model in AIModel})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reset_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "openai_api_keys"

    @before_event(Update, Replace)
    def before_update(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def can_use(self, tokens: int, model: AIModel) -> bool:
        if not self.status == OpenAiClientStatus.ACTIVE:
            return False
        
        if self.model_usage.get(model, 0) + tokens > MODEL_MAX_BATCH_QUEUE_LIMIT_PER_PROJECT_TPD[model]:
            return False
        
        return True
    
    def register_usage(self, model: AIModel, tokens: int) -> int:
        self.model_usage[model] = self.model_usage.get(model, 0) + tokens
        return self.model_usage[model]