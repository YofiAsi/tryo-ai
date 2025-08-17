import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from beanie import PydanticObjectId
from fastapi import Depends

from app.conf.page_response import PageResponse
from app.entity.activity_log_entity import ActivityLog, ActivityType
from app.entity.user_entity import User
from app.repository.activity_log_repository import ActivityLogRepository
from app.repository.user_repository import UserRepository
from app.schema.activity_log_dto import (
    CreateActivityLogDTO, 
    UpdateActivityLogDTO, 
    ActivityLogDTO, 
    ActivityLogFilterDTO,
    ActivityLogSummaryDTO
)
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class ActivityLogService:
    """
    Activity Log Business Logic Service that is responsible for handling business logic for ActivityLog entity operations.

    Attributes:
    activity_log_repository: ActivityLogRepository
        Repository for ActivityLog entity operations
    user_repository: UserRepository
        Repository for User entity operations
    """

    def __init__(self, 
                 activity_log_repository: ActivityLogRepository = Depends(),
                 user_repository: UserRepository = Depends()):
        _log.info("ActivityLogService Initializing")
        self.repository = activity_log_repository
        self.user_repository = user_repository

    async def retrieve(self, activity_log_id: PydanticObjectId) -> Optional[ActivityLogDTO]:
        _log.debug(f"ActivityLogService Retrieving activity log: {activity_log_id}")
        
        final_activity_log = await self.repository.retrieve(activity_log_id)
        if final_activity_log is None:
            _log.error("ActivityLogService Activity log not found")
            return None
        
        result = ActivityLogDTO.model_validate(final_activity_log)
        _log.debug("ActivityLogService Activity log retrieved")
        return result

    async def find(self, query: dict, page: int, size: int, sort: str = "_id") -> PageResponse[ActivityLogDTO]:
        _log.debug("ActivityLogService list request")
        entity_page_response = await self.repository.find(query, page, size, sort)
        page_response = PageResponse[ActivityLogDTO](
            content=[ActivityLogDTO.model_validate(log) for log in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug("ActivityLogService Activity logs retrieved")
        return page_response

    async def find_with_filters(
        self,
        user_id: Optional[PydanticObjectId] = None,
        activity_type: Optional[ActivityType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> PageResponse[ActivityLogDTO]:
        _log.debug("ActivityLogService Getting activity logs with filters")
        
        entity_page_response = await self.repository.find_with_filters(
            user_id=user_id,
            activity_type=activity_type,
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address,
            page=page,
            size=size
        )
        
        page_response = PageResponse[ActivityLogDTO](
            content=[ActivityLogDTO.model_validate(log) for log in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug(f"ActivityLogService Retrieved {len(page_response.content)} activity logs")
        return page_response

    async def find_by_user(
        self,
        user_id: PydanticObjectId,
        page: int = 1,
        size: int = 10
    ) -> PageResponse[ActivityLogDTO]:
        _log.debug(f"ActivityLogService Getting activity logs for user: {user_id}")
        
        # Validate user exists
        user = await self.user_repository.retrieve(user_id)
        if not user:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {user_id}")
        
        entity_page_response = await self.repository.find_by_user(user_id, page, size)
        page_response = PageResponse[ActivityLogDTO](
            content=[ActivityLogDTO.model_validate(log) for log in entity_page_response.content],
            page=entity_page_response.page,
            size=entity_page_response.size,
            total=entity_page_response.total,
        )

        _log.debug(f"ActivityLogService Retrieved {len(page_response.content)} activity logs for user {user_id}")
        return page_response

    async def delete(self, activity_log_id: PydanticObjectId):
        _log.debug(f"ActivityLogService Deleting activity log: {activity_log_id}")
        
        await self.repository.delete(activity_log_id)
        _log.debug("ActivityLogService Activity log deleted")

    async def count(self, query: dict) -> int:
        _log.debug(f"ActivityLogService Counting activity logs with query: {query}")
        result = await self.repository.count(query)
        _log.debug(f"ActivityLogService Activity logs counted: {result}")
        return result

    async def create(self, activity_log_data: CreateActivityLogDTO) -> ActivityLogDTO:
        _log.debug(f"ActivityLogService Creating activity log: {activity_log_data.activity_type}")
        
        # Validate user exists if user_id is provided
        user = None
        if activity_log_data.user_id:
            user = await self.user_repository.retrieve(activity_log_data.user_id)
            if not user:
                raise BusinessException(ErrorCodes.NOT_FOUND, f"User not found: {activity_log_data.user_id}")
        
        # Create activity log entry
        activity_log = ActivityLog(
            user=user,
            activity_type=activity_log_data.activity_type,
            data=activity_log_data.data,
            ip_address=activity_log_data.ip_address,
            user_agent=activity_log_data.user_agent
        )
        
        created_activity_log = await self.repository.create(activity_log)
        result = ActivityLogDTO.model_validate(created_activity_log)
        _log.debug(f"ActivityLogService Activity log created: {result.id}")
        return result

    async def log_user_activity(
        self,
        user: User,
        activity_type: ActivityType,
        data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLogDTO:
        _log.debug(f"ActivityLogService Logging user activity: {activity_type} for user: {user.email}")
        
        # Create activity log entry
        activity_log = ActivityLog(
            user=user,
            activity_type=activity_type,
            data=data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        created_activity_log = await self.repository.create(activity_log)
        result = ActivityLogDTO.model_validate(created_activity_log)
        _log.debug(f"ActivityLogService User activity logged: {result.id}")
        return result

    async def update(self, activity_log_id: PydanticObjectId, update_data: UpdateActivityLogDTO) -> ActivityLogDTO:
        _log.debug(f"ActivityLogService Updating activity log: {activity_log_id}")
        
        # Get existing activity log
        activity_log = await self.repository.retrieve(activity_log_id)
        if not activity_log:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Activity log not found: {activity_log_id}")
        
        # Update fields if provided
        if update_data.data is not None:
            activity_log.data = update_data.data
        if update_data.ip_address is not None:
            activity_log.ip_address = update_data.ip_address
        if update_data.user_agent is not None:
            activity_log.user_agent = update_data.user_agent
        
        updated_activity_log = await self.repository.update(activity_log)
        result = ActivityLogDTO.model_validate(updated_activity_log)
        _log.debug(f"ActivityLogService Activity log updated: {result.id}")
        return result

    async def get_activity_summary(self, days: int = 30) -> ActivityLogSummaryDTO:
        _log.debug(f"ActivityLogService Getting activity summary for last {days} days")
        
        summary_data = await self.repository.get_activity_summary(days)
        
        # Convert recent activities to DTOs
        recent_activities = [ActivityLogDTO.model_validate(log) for log in summary_data["recent_activities"]]
        
        # Create summary DTO
        summary = ActivityLogSummaryDTO(
            total_activities=summary_data["total_activities"],
            activities_by_type=summary_data["activities_by_type"],
            activities_by_user=summary_data["activities_by_user"],
            recent_activities=recent_activities
        )
        
        _log.debug(f"ActivityLogService Generated summary: {summary.total_activities} total activities")
        return summary

    async def cleanup_old_logs(self, days: int = 90) -> int:
        _log.debug(f"ActivityLogService Cleaning up logs older than {days} days")
        
        deleted_count = await self.repository.delete_old_logs(days)
        _log.debug(f"ActivityLogService Cleaned up {deleted_count} old logs")
        return deleted_count
