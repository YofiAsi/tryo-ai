"""
AI Agents API endpoints for TyroHR backend.

This module provides REST API endpoints for interacting with AI agents
including job position analysis, candidate screening, and other AI-powered features.
"""

import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.conf.dependencies import get_current_active_user, get_ai_agents_service
from app.entity.user_entity import User
from app.service.ai_agents_service import AIAgentsService
from app.conf.app_settings import server_settings
from app.api.api_response import response_fail_status_codes
from app.schema.ai_agents_dto import JobPositionChatRequest, JobPositionChatResponse, JobPositionChatServiceRequest
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python


_resource = "ai-agents"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
                   # dependencies=[Depends(auth_handler.get_token_user)],
                   responses=response_fail_status_codes
                   )



@router.post("/job-position/chat",
             operation_id="chat_with_job_analyzer",
             name="chat_with_job_analyzer",
             summary="Chat with job position analyzer",
             response_model=JobPositionChatResponse,
             status_code=status.HTTP_200_OK)
async def chat_with_job_analyzer(
    request: JobPositionChatRequest,
    ai_service: AIAgentsService = Depends(get_ai_agents_service)
) -> JobPositionChatResponse:
    """
    Chat with the Job Position Analyzer Agent.
    
    Args:
        request: Chat request containing the message and message history
        
    Returns:
        Chat response from the AI agent with output and updated message history
    """
    try:
        service_request = JobPositionChatServiceRequest(
            message=request.message,
            message_history=None
        )

        if request.message_history is not None:
            service_request.message_history = ModelMessagesTypeAdapter.validate_python(json.loads(request.message_history))

        result = await ai_service.job_position_chat(service_request)
        _log.info("Job position chat completed")
        
        response= JobPositionChatResponse(
            output=result.output,
            message_history=json.dumps(to_jsonable_python(result.message_history))
        )
        return response
    except Exception as e:
        _log.error(f"Error in job position chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chat with job analyzer: {str(e)}"
        )
