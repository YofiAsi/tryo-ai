from datetime import datetime
from typing import Optional, Any, Dict

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict

from app.entity.activity_log_entity import ActivityType
from app.schema.base_dto import BaseModelJsonSerializable
from app.schema.user_dto import UserDTO


class CreateActivityLogDTO(BaseModelJsonSerializable):
    """DTO for creating a new activity log entry"""
    user_id: Optional[PydanticObjectId] = Field(None, description="ID of the user who performed the activity (None for system events)")
    activity_type: ActivityType = Field(..., description="Type of activity performed")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data related to the activity")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    model_config = ConfigDict(
        title="Create Activity Log Request",
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "activity_type": "login",
                "data": {"login_method": "google_oauth", "success": True},
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        }
    )


class UpdateActivityLogDTO(BaseModelJsonSerializable):
    """DTO for updating an existing activity log entry"""
    data: Optional[Dict[str, Any]] = Field(None, description="Updated data for the activity")
    ip_address: Optional[str] = Field(None, description="Updated IP address")
    user_agent: Optional[str] = Field(None, description="Updated user agent string")
    
    model_config = ConfigDict(
        title="Update Activity Log Request",
        json_schema_extra={
            "example": {
                "data": {"additional_info": "Updated activity data"},
                "ip_address": "192.168.1.2"
            }
        }
    )


class ActivityLogDTO(BaseModelJsonSerializable):
    """DTO for returning activity log data"""
    id: PydanticObjectId = Field(..., description="Activity log ID")
    user: Optional[UserDTO] = Field(None, description="User who performed the activity")
    activity_type: ActivityType = Field(..., description="Type of activity performed")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data related to the activity")
    date: datetime = Field(..., description="Timestamp of the activity")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    model_config = ConfigDict(
        from_attributes=True,
        title="Activity Log Response",
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "user_email": "user@example.com",
                "user_name": "John Doe",
                "activity_type": "login",
                "data": {"login_method": "google_oauth", "success": True},
                "date": "2024-01-01T12:00:00Z",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        }
    )


class ActivityLogFilterDTO(BaseModelJsonSerializable):
    """DTO for filtering activity logs"""
    user_id: Optional[PydanticObjectId] = Field(None, description="Filter by specific user ID (None for all users)")
    activity_type: Optional[ActivityType] = Field(None, description="Filter by activity type")
    start_date: Optional[datetime] = Field(None, description="Filter activities from this date")
    end_date: Optional[datetime] = Field(None, description="Filter activities until this date")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")
    
    model_config = ConfigDict(
        title="Activity Log Filter Request",
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "activity_type": "login",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z"
            }
        }
    )


class ActivityLogSummaryDTO(BaseModelJsonSerializable):
    """DTO for activity log summary statistics"""
    total_activities: int = Field(..., description="Total number of activities")
    activities_by_type: Dict[str, int] = Field(..., description="Count of activities by type")
    activities_by_user: Dict[str, int] = Field(..., description="Count of activities by user")
    recent_activities: list[ActivityLogDTO] = Field(..., description="List of recent activities")
    
    model_config = ConfigDict(
        title="Activity Log Summary Response",
        json_schema_extra={
            "example": {
                "total_activities": 150,
                "activities_by_type": {
                    "login": 45,
                    "new_candidate": 12,
                    "update_candidate": 8
                },
                "activities_by_user": {
                    "user1@example.com": 25,
                    "user2@example.com": 18
                },
                "recent_activities": []
            }
        }
    )
