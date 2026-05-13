"""
AI Agents DTO schemas for TyroHR backend API.

This module contains Pydantic models for AI agent interactions including
job position chat requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai.messages import ModelMessage

from app.schema.base_dto import BaseModelJsonSerializable


class JobPositionChatServiceRequest(BaseModelJsonSerializable):
    """
    Request DTO for job position chat interactions.

    This model represents the input for a chat session with the job position analyzer agent.
    """

    message: str = Field(
        ...,
        description="The user's message to the job position analyzer agent",
        min_length=1,
        max_length=10000
    )

    message_history: Optional[List[ModelMessage]] = Field(
        default=None,
        description="List of previous messages in the conversation for context"
    )

    model: Optional[str] = Field(
        default=None,
        description="LiteLLM model id (e.g. 'gpt-4o', 'claude-sonnet-4-5', 'ollama/llama3.1'). Falls back to server default when None."
    )


class JobPositionChatServiceResponse(BaseModelJsonSerializable):
    """
    Response DTO for job position chat interactions.
    
    This model represents the output from a chat session with the job position analyzer agent.
    """
    
    output: str = Field(
        ...,
        description="The AI agent's response to the user's message"
    )
    
    message_history: Optional[List[ModelMessage]] = Field(
        default=None,
        description="Updated list of messages including the new conversation turn"
    )


class JobPositionChatRequest(BaseModelJsonSerializable):
    """
    Request DTO for job position chat interactions.
    
    This model represents the input for a chat session with the job position analyzer agent.
    """
    
    message: str = Field(
        ...,
        description="The user's message to the job position analyzer agent",
        min_length=1,
        max_length=10000
    )
    
    message_history: str = Field(
        default=None,
        description="List of previous messages in the conversation for context in json format"
    )

    model: Optional[str] = Field(
        default=None,
        description="LiteLLM model id (e.g. 'gpt-4o', 'claude-sonnet-4-5', 'ollama/llama3.1'). Falls back to server default when None."
    )


class JobPositionChatResponse(BaseModelJsonSerializable):
    """
    Response DTO for job position chat interactions.
    
    This model represents the output from a chat session with the job position analyzer agent.
    """
    
    output: str = Field(
        ...,
        description="The AI agent's response to the user's message"
    )
    
    message_history: str = Field(
        default=None,
        description="List of previous messages in the conversation for context in json format"
    )


class JobPositionAnalyzerServiceRequest(BaseModelJsonSerializable):
    """
    Request DTO for job position analyzer interactions.

    This model represents the input for a job position analyzer session.
    """

    message_history: Optional[List[ModelMessage]] = Field(
        default=None,
        description="List of previous messages in the conversation for context"
    )

    model: Optional[str] = Field(
        default=None,
        description="LiteLLM model id. Falls back to server default when None."
    )


class JobPositionAnalyzerRequest(BaseModelJsonSerializable):
    """
    Request DTO for job position analyzer interactions.

    This model represents the input for a job position analyzer session.
    """

    message_history: str = Field(
        default=None,
        description="List of previous messages in the conversation for context in json format"
    )

    model: Optional[str] = Field(
        default=None,
        description="LiteLLM model id. Falls back to server default when None."
    )

