"""LLM model catalog endpoint.

Thin proxy over LiteLLM's `/v1/models`. The frontend uses this to populate the
model picker — including Ollama models discovered live from the local server.
"""

import logging
import os
from typing import Any, List

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.api_response import response_fail_status_codes
from app.conf.app_settings import llm_settings, server_settings

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "").rstrip("/")

_resource = "llm"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(
    prefix=_path,
    tags=[_resource],
    responses=response_fail_status_codes,
)


class LLMModel(BaseModel):
    id: str


class LLMCatalogResponse(BaseModel):
    models: List[LLMModel]
    default_chat: str
    default_analyzer: str


async def _fetch_litellm_models(client: httpx.AsyncClient) -> List[str]:
    url = f"{llm_settings.BASE_URL}/v1/models"
    headers = {"Authorization": f"Bearer {llm_settings.MASTER_KEY}"} if llm_settings.MASTER_KEY else {}
    resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    payload: Any = resp.json()
    raw = payload.get("data", []) if isinstance(payload, dict) else []
    return [item["id"] for item in raw if isinstance(item, dict) and item.get("id") and "*" not in item["id"]]


async def _fetch_ollama_models(client: httpx.AsyncClient) -> List[str]:
    if not OLLAMA_BASE_URL:
        return []
    try:
        resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
        payload: Any = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        _log.warning(f"Failed to fetch Ollama tags from {OLLAMA_BASE_URL}: {e}")
        return []
    tags = payload.get("models", []) if isinstance(payload, dict) else []
    return [f"ollama/{m['name']}" for m in tags if isinstance(m, dict) and m.get("name")]


@router.get(
    "/models",
    operation_id="list_llm_models",
    name="list_llm_models",
    summary="List models available through the LiteLLM proxy",
    response_model=LLMCatalogResponse,
    status_code=status.HTTP_200_OK,
)
async def list_llm_models() -> LLMCatalogResponse:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            litellm_ids = await _fetch_litellm_models(client)
            ollama_ids = await _fetch_ollama_models(client)
    except (httpx.HTTPError, ValueError) as e:
        _log.error(f"Failed to fetch LiteLLM model catalog: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model catalog unavailable",
        )

    seen: set[str] = set()
    merged: List[str] = []
    for mid in [*litellm_ids, *ollama_ids]:
        if mid not in seen:
            seen.add(mid)
            merged.append(mid)

    return LLMCatalogResponse(
        models=[LLMModel(id=mid) for mid in merged],
        default_chat=llm_settings.DEFAULT_CHAT_MODEL,
        default_analyzer=llm_settings.DEFAULT_ANALYZER_MODEL,
    )
