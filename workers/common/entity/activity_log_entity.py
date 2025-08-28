from datetime import datetime, timezone
from typing import Optional, Any, Dict
from enum import Enum

from beanie import Document, Link
from pydantic import BaseModel, Field

from entity.user_entity import User


class ActivityType(str, Enum):
    """Types of activities that can be logged"""
    LOGIN = "login"
    LOGOUT = "logout"
    NEW_CANDIDATE = "new_candidate"
    UPDATE_CANDIDATE = "update_candidate"
    DELETE_CANDIDATE = "delete_candidate"
    NEW_JOB_POSITION = "new_job_position"
    UPDATE_JOB_POSITION = "update_job_position"
    DELETE_JOB_POSITION = "delete_job_position"
    CHANGE_CANDIDATE_STATUS = "change_candidate_status"
    CHANGE_JOB_POSITION_STATUS = "change_job_position_status"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    SYSTEM_EVENT = "system_event"
    ERROR_EVENT = "error_event"


class ActivityLog(Document):
    """
    Activity Log entity for tracking user actions and system events.
    
    This entity logs various activities such as:
    - User authentication (login/logout)
    - CRUD operations on candidates and job positions
    - Status changes
    - System events and errors
    """
    
    user: Optional[Link[User]] = Field(None, description="User who performed the activity (None for system events)")
    activity_type: ActivityType = Field(..., description="Type of activity performed")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data related to the activity")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the activity")
    ip_address: Optional[str] = Field(None, description="IP address of the user (for security tracking)")
    user_agent: Optional[str] = Field(None, description="User agent string (for security tracking)")
    
    class Settings:
        name = "activity_logs"
        validate_on_save = True
        indexes = [
            "user",
            "activity_type", 
            "date",
            ("user", "date"),
            ("activity_type", "date")
        ]
    
    def __str__(self):
        user_info = f"User: {self.user.id}" if self.user else "System"
        return f"ActivityLog: {user_info}, {self.activity_type}, {self.date}"
    
    @classmethod
    async def log_activity(
        cls,
        user: Optional[User] = None,
        activity_type: ActivityType = None,
        data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> "ActivityLog":
        """
        Convenience method to create and save an activity log entry.
        
        Args:
            user: User who performed the activity
            activity_type: Type of activity
            data: Additional data for the activity
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            ActivityLog: The created activity log entry
        """
        activity_log = cls(
            user=user,
            activity_type=activity_type,
            data=data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return await activity_log.insert()
