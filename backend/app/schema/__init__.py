"""
Schema package for TyroHR backend API.

This package contains all DTO (Data Transfer Object) schemas used throughout the application.
"""

from .ai_agents_dto import (
    JobPositionChatRequest,
    JobPositionChatResponse,
    JobPositionChatServiceResponse
)

__all__ = [
    "JobPositionChatRequest",
    "JobPositionChatResponse", 
    "JobPositionChatServiceResponse"
]
