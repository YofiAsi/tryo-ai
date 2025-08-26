import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Tuple, Generator, Optional
from openai import OpenAI
from app.entity.openai_client_entity import OpenAiClient

@dataclass
class OpenAiClientContext:
    name: str
    sdk: OpenAI
    document: OpenAiClient


class OpenAiSdkClient:
    def __init__(self, api_key: str, document: OpenAiClient):
        self._sdk = OpenAI(api_key=api_key)
        self._document: OpenAiClient = document
        self._lock = threading.Lock()

    @contextmanager
    def access_client(
        self,
        blocking: bool = True,
        timeout: float = -1,  # threading.Lock expects float or -1
    ) -> Generator[Optional[OpenAiClientContext], None, None]:

        acquired = self._lock.acquire(blocking=blocking, timeout=timeout)
        if not acquired:
            yield None
            return
        try:
            yield OpenAiClientContext(self.get_name(), self._sdk, self._document)
        finally:
            self._lock.release()
    
    def get_client_no_lock(self) -> OpenAI:
        """
        Used only for actions that don't input tokens, like downloading files.
        """
        return self._sdk
    
    def get_name(self) -> str:
        return self._document.name

    

