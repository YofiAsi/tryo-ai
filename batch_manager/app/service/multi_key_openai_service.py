"""
MultiKeyOpenAiClientService for managing multiple OpenAI clients with different API keys.
"""

from __future__ import annotations

import os
import random
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable, Dict, Generator, Generic, List, Optional, TypeVar

from app.entity.openai_client_entity import OpenAiClient
from app.infrastructure.openai_sdk_wrapper import OpenAiClientContext, OpenAiSdkClient

if TYPE_CHECKING:
    from openai import OpenAI

    from app.consts.ai_models import AIModel
    from app.repository.openai_client_repository import OpenAiClientRepository

T = TypeVar("T")

class NoAvailableClient(Exception):
    def __init__(self, tokens: int, model: AIModel):
        self.tokens = tokens
        self.model = model
        super().__init__(f"No client available with enough tokens for model {model} and tokens {tokens}")

@dataclass
class MultiKeyOpenAiClientServiceResponse(Generic[T]):
    client_name: str
    response: T

class MultiKeyOpenAiClientService:
    def __init__(self, openai_client_repository: OpenAiClientRepository):
        self.clients_by_name: Dict[str, OpenAiSdkClient] = {}
        self.rotation_lock = threading.Lock()
        self.client_names: List[str] = []
        self.current_index = 0
        self.openai_client_repository = openai_client_repository
        self._initialized = False

    async def init_clients(self) -> None:
        if self._initialized:
            return
            
        names_keys = {
            name: key for name, key in os.environ.items()
            if name.startswith("BATCH_OPENAI_API_KEY_") and key
        }
        
        for name, key in names_keys.items():
            document = await self.openai_client_repository.retrieve_by_name(name)
            if not document:
                document = await self.openai_client_repository.create(
                    OpenAiClient(name=name)
                )
            
            self.clients_by_name[name] = OpenAiSdkClient(key, document)
            self.client_names.append(name)
            
        self._initialized = True

    async def reset_usage_if_needed(self) -> None:
        now = datetime.now(timezone.utc)
        last_midnight = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0, microsecond=0)
        for client in self.clients_by_name.values():
            with client.access_client() as client_context:
                if not client_context:
                    continue
                if client_context.document.last_reset_at >= last_midnight:
                    continue
                await self.openai_client_repository.reset_daily_usage(client_context.document.name)

    @contextmanager
    def get_client(self, tokens: int, model: AIModel) -> Generator[Optional[OpenAiClientContext], None, None]:
        if not self._initialized:
            raise RuntimeError("MultiKeyOpenAiClientService not initialized. Call init_clients() during server startup.")
            
        self.rotation_lock.acquire()
        released = False
        try:
            for _ in range(len(self.client_names)):
                name = self.client_names[self.current_index]
                client = self.clients_by_name[name]
                self.current_index = (self.current_index + 1) % len(self.client_names)

                try:
                    with client.access_client(blocking=False) as client_context:
                        if not client_context:
                            continue
                        if client_context.document.can_use(tokens, model):
                            self.rotation_lock.release()
                            released = True
                            yield client_context
                            return
                except RuntimeError:
                    continue

            yield None
        finally:
            if not released:
                self.rotation_lock.release()

    def _execute_with_backoff(
        self,
        client: OpenAI,
        operation_func: Callable[[OpenAI], T],
    ) -> T:
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                result = operation_func(client)
                return result
            except Exception as e:
                if "rate limit" in str(e).lower():
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    raise
        raise Exception("Max retries exceeded")

    async def execute(self, tokens: int, model: AIModel, operation_func: Callable[[OpenAI], T]) -> MultiKeyOpenAiClientServiceResponse[T]:
        with self.get_client(tokens, model) as client_context:
            if not client_context:
                raise NoAvailableClient(tokens, model)
            response = self._execute_with_backoff(client_context.sdk, operation_func)
            if response:
                client_context.document.register_usage(model, tokens)
                await self.openai_client_repository.update(client_context.document)
            return MultiKeyOpenAiClientServiceResponse(client_name=client_context.name, response=response)
    
    def execute_with_client_name_no_tokens(self, client_name: str, operation_func: Callable[[OpenAI], T]) -> MultiKeyOpenAiClientServiceResponse[T]:
        if not self._initialized:
            raise RuntimeError("MultiKeyOpenAiClientService not initialized. Call init_clients() during server startup.")
            
        if client_name not in self.clients_by_name:
            raise Exception("Invalid client name")
        
        client = self.clients_by_name[client_name].get_client_no_lock()
        response = self._execute_with_backoff(client, operation_func)
        return MultiKeyOpenAiClientServiceResponse(client_name=client_name, response=response)