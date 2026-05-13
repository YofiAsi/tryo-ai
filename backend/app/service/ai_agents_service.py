"""
AI Agents Service for TyroHR backend API.

This service manages AI agents and provides a unified interface for
interacting with different types of AI agents in the system.
"""

import logging
from typing import Any, Dict

from openai import AsyncOpenAI
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import ModelMessage

from app.ai_agents.job_position_chat import get_job_position_chat_agent
from app.ai_agents.job_position_analyzer import get_job_position_analyzer_agent

from app.conf.app_settings import openai_settings
from app.schema.ai_agents_dto import JobPositionChatServiceRequest, JobPositionChatServiceResponse, JobPositionAnalyzerServiceRequest
from app.schema.job_position_dto import CreateJobPositionDTO

_log = logging.getLogger(__name__)


class AIAgentsService:
    """
    Service class for managing AI agents.
    
    This service provides methods to interact with various AI agents
    and handles agent lifecycle management.
    """
    
    def __init__(self):
        """
        Initialize the AI Agents Service.
        """
        self._job_position_chat_agent = None
        self._job_position_analyzer_agent = None
        self.openai_client = AsyncOpenAI(
            api_key=openai_settings.API_KEY,
            max_retries=3,
            timeout=60
        )
    
    def get_job_position_chat_agent(self):
        """
        Get or create the Job Position Analyzer Agent.
        
        Returns:
            Job Position Analyzer Agent instance
        """
        model = OpenAIModel('gpt-4o', settings=ModelSettings(temperature=0.0, max_tokens=16384), provider=OpenAIProvider(openai_client=self.openai_client))

        if self._job_position_chat_agent is None:
            self._job_position_chat_agent = get_job_position_chat_agent(model)
        return self._job_position_chat_agent
    
    def get_job_position_analyzer_agent(self):
        """
        Get or create the Job Position Analyzer Agent.
        
        Returns:
            Job Position Analyzer Agent instance
        """
        model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(openai_client=self.openai_client))

        if self._job_position_analyzer_agent is None:
            self._job_position_analyzer_agent = get_job_position_analyzer_agent(model)
        return self._job_position_analyzer_agent
    
    async def job_position_analyzer(self, request: JobPositionAnalyzerServiceRequest) -> CreateJobPositionDTO:
        """
        Analyze the job position.
        
        Args:
            request: JobPositionAnalyzerServiceRequest containing the message and message history
            
        Returns:
            CreateJobPositionDTO containing the agent output and updated message history
        """
        agent = self.get_job_position_analyzer_agent()
        result = await agent.run("Please parse the data", message_history=request.message_history)
        _log.info("Job position analyzer completed successfully")

        return result.output

    
    async def job_position_chat(self, request: JobPositionChatServiceRequest) -> JobPositionChatServiceResponse:
        """
        Chat with the Job Position Analyzer Agent.
        
        Args:
            message: The message to chat with the agent
            message_history: List of previous messages in the conversation
            
        Returns:
            JobPositionChatResponse containing the agent output and updated message history
        """
        try:
            agent = self.get_job_position_chat_agent()
            result = await agent.run(request.message, message_history=request.message_history)
            _log.info("Job position chat completed successfully")

            return JobPositionChatServiceResponse(
                output=result.output,
                message_history=result.all_messages()
            )
        except Exception as e:  
            _log.error(f"Error in job position chat: {str(e)}")
            # Return error response with empty output and original message history
            return JobPositionChatServiceResponse(
                output=f"Error: {str(e)}",
                message_history=request.message_history
            )