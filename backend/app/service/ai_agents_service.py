"""
AI Agents Service for TyroHR backend API.

This service manages AI agents and provides a unified interface for
interacting with different types of AI agents in the system.
"""

import logging

from app.ai_agents.job_position_chat import get_job_position_chat_agent
from app.ai_agents.job_position_analyzer import get_job_position_analyzer_agent
from app.ai_agents.model_factory import build_model

from app.conf.app_settings import llm_settings
from app.schema.ai_agents_dto import (
    JobPositionChatServiceRequest,
    JobPositionChatServiceResponse,
    JobPositionAnalyzerServiceRequest,
)
from app.schema.job_position_dto import CreateJobPositionDTO

_log = logging.getLogger(__name__)


class AIAgentsService:
    """Service class for managing AI agents.

    Agents are constructed per request so the caller can pick a different model
    each time (frontend-driven model selection via the LiteLLM proxy).
    """

    def __init__(self):
        self._settings = llm_settings

    def _chat_agent(self, model_name: str | None):
        model = build_model(
            model_name or self._settings.DEFAULT_CHAT_MODEL,
            self._settings,
            temperature=0.0,
            max_tokens=16384,
        )
        return get_job_position_chat_agent(model)

    def _analyzer_agent(self, model_name: str | None):
        model = build_model(
            model_name or self._settings.DEFAULT_ANALYZER_MODEL,
            self._settings,
        )
        return get_job_position_analyzer_agent(model)

    async def job_position_analyzer(self, request: JobPositionAnalyzerServiceRequest) -> CreateJobPositionDTO:
        agent = self._analyzer_agent(request.model)
        result = await agent.run("Please parse the data", message_history=request.message_history)
        _log.info("Job position analyzer completed successfully")
        return result.output

    async def job_position_chat(self, request: JobPositionChatServiceRequest) -> JobPositionChatServiceResponse:
        try:
            agent = self._chat_agent(request.model)
            result = await agent.run(request.message, message_history=request.message_history)
            _log.info("Job position chat completed successfully")
            return JobPositionChatServiceResponse(
                output=result.output,
                message_history=result.all_messages(),
            )
        except Exception as e:
            _log.error(f"Error in job position chat: {str(e)}")
            return JobPositionChatServiceResponse(
                output=f"Error: {str(e)}",
                message_history=request.message_history,
            )
