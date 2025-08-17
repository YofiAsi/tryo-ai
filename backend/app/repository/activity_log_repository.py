import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from beanie import PydanticObjectId

from app.conf.page_response import PageResponse
from app.entity.activity_log_entity import ActivityLog, ActivityType
from app.entity.user_entity import User
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class ActivityLogRepository:
    """
    Activity Log Repository class
    
    This class is responsible for handling all the database operations related to the ActivityLog entity.
    ActivityLog entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self):
        _log.debug("ActivityLogRepository initialized")

    async def create(self, activity_log: ActivityLog) -> ActivityLog:
        """Create a new activity log entry"""
        _log.debug(f"ActivityLogRepository Creating activity log: {activity_log}")
        result = await ActivityLog.insert(activity_log)
        _log.debug("ActivityLogRepository Activity log created")
        return result

    async def retrieve(self, id: PydanticObjectId) -> Optional[ActivityLog]:
        """Find an activity log by ID"""
        _log.debug(f"ActivityLogRepository Finding activity log by ID: {id}")
        result = await ActivityLog.find_one({"_id": id})
        _log.debug("ActivityLogRepository Activity log found")
        return result

    async def find(self, query: dict, page: int = 1, size: int = 10, sort: str = "_id") -> PageResponse:
        """Find activity logs with pagination"""
        _log.debug("ActivityLogRepository list request")
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page index")

        total_count = await ActivityLog.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        content = await ActivityLog.find(query).skip((page-1) * size).limit(size).sort(sort).to_list()
        
        # Fetch links for each document if needed
        for activity_log in content:
            if activity_log.user:
                await activity_log.fetch_link("user")
        
        _log.debug(f"ActivityLogRepository Found {len(content)} activity logs")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count(self, query: dict) -> int:
        """Count activity logs with query"""
        _log.debug(f"ActivityLogRepository Counting activity logs with query: {query}")
        result = await ActivityLog.find(query).count()
        _log.debug(f"ActivityLogRepository Activity logs counted: {result}")
        return result

    async def find_by_user(self, user_id: PydanticObjectId, page: int = 1, size: int = 10) -> PageResponse:
        """Find activity logs for a specific user with pagination"""
        _log.debug(f"ActivityLogRepository Finding activity logs for user: {user_id}")
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page index")

        total_count = await ActivityLog.find({"user": user_id}).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        content = await ActivityLog.find({"user": user_id}).skip((page-1) * size).limit(size).sort("-date").to_list()
        
        # Fetch links for each document if needed
        for activity_log in content:
            if activity_log.user:
                await activity_log.fetch_link("user")
        
        _log.debug(f"ActivityLogRepository Found {len(content)} activity logs for user {user_id}")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_activity_type(self, activity_type: ActivityType, page: int = 1, size: int = 10) -> PageResponse:
        """Find activity logs by activity type with pagination"""
        _log.debug(f"ActivityLogRepository Finding activity logs by type: {activity_type}")
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page index")

        total_count = await ActivityLog.find({"activity_type": activity_type}).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        content = await ActivityLog.find({"activity_type": activity_type}).skip((page-1) * size).limit(size).sort("-date").to_list()
        
        # Fetch links for each document if needed
        for activity_log in content:
            if activity_log.user:
                await activity_log.fetch_link("user")
        
        _log.debug(f"ActivityLogRepository Found {len(content)} activity logs for type {activity_type}")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_date_range(self, start_date: datetime, end_date: datetime, page: int = 1, size: int = 10) -> PageResponse:
        """Find activity logs within a date range with pagination"""
        _log.debug(f"ActivityLogRepository Finding activity logs from {start_date} to {end_date}")
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page index")

        query = {
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        total_count = await ActivityLog.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        content = await ActivityLog.find(query).skip((page-1) * size).limit(size).sort("-date").to_list()
        
        # Fetch links for each document if needed
        for activity_log in content:
            if activity_log.user:
                await activity_log.fetch_link("user")
        
        _log.debug(f"ActivityLogRepository Found {len(content)} activity logs in date range")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_with_filters(
        self,
        user_id: Optional[PydanticObjectId] = None,
        activity_type: Optional[ActivityType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> PageResponse:
        """Find activity logs with multiple filters and pagination"""
        _log.debug("ActivityLogRepository Finding activity logs with filters")
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page index")

        # Build query based on filters
        query = {}
        
        if user_id:
            query["user"] = user_id
        
        if activity_type:
            query["activity_type"] = activity_type
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["date"] = date_query
        
        if ip_address:
            query["ip_address"] = ip_address
        


        total_count = await ActivityLog.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        content = await ActivityLog.find(query).skip((page-1) * size).limit(size).sort("-date").to_list()
        for doc in content:
            await doc.fetch_link(ActivityLog.user)
        _log.info(content)
                
        
        _log.debug(f"ActivityLogRepository Found {len(content)} activity logs with filters")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def get_recent_activities(self, limit: int = 10) -> List[ActivityLog]:
        """Get the most recent activity logs"""
        _log.debug(f"ActivityLogRepository Getting recent {limit} activities")
        
        content = await ActivityLog.find().sort("-date").limit(limit).to_list()
        
        # Fetch links for each document if needed
        for activity_log in content:
            if activity_log.user:
                await activity_log.fetch_link("user")
        
        _log.debug(f"ActivityLogRepository Retrieved {len(content)} recent activities")
        return content

    async def get_activity_summary(self, days: int = 30) -> dict:
        """Get summary statistics for activities in the last N days"""
        _log.debug(f"ActivityLogRepository Getting activity summary for last {days} days")
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get total count
        total_count = await ActivityLog.find({"date": {"$gte": start_date}}).count()
        
        # Get count by activity type
        pipeline = [
            {"$match": {"date": {"$gte": start_date}}},
            {"$group": {"_id": "$activity_type", "count": {"$sum": 1}}}
        ]
        activities_by_type = {}
        async for result in ActivityLog.aggregate(pipeline):
            activities_by_type[result["_id"]] = result["count"]
        
        # Get count by user
        pipeline = [
            {"$match": {"date": {"$gte": start_date}, "user": {"$exists": True, "$ne": None}}},
            {"$lookup": {"from": "users", "localField": "user", "foreignField": "_id", "as": "user_info"}},
            {"$unwind": "$user_info"},
            {"$group": {"_id": "$user_info.email", "count": {"$sum": 1}}}
        ]
        activities_by_user = {}
        async for result in ActivityLog.aggregate(pipeline):
            activities_by_user[result["_id"]] = result["count"]
        
        # Get recent activities
        recent_activities = await self.get_recent_activities(10)
        
        summary = {
            "total_activities": total_count,
            "activities_by_type": activities_by_type,
            "activities_by_user": activities_by_user,
            "recent_activities": recent_activities
        }
        
        _log.debug(f"ActivityLogRepository Generated summary: {total_count} total activities")
        return summary

    async def delete_old_logs(self, days: int = 90) -> int:
        """Delete activity logs older than specified days (for data cleanup)"""
        _log.debug(f"ActivityLogRepository Deleting logs older than {days} days")
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        result = await ActivityLog.find({"date": {"$lt": cutoff_date}}).delete()
        
        _log.debug(f"ActivityLogRepository Deleted {result} old activity logs")
        return result

    async def update(self, activity_log: ActivityLog) -> Optional[ActivityLog]:
        """Update an existing activity log entry"""
        _log.debug(f"ActivityLogRepository Updating activity log: {activity_log.id}")
        
        if activity_log.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Activity log ID is required for update")
        
        result = await activity_log.replace()
        _log.debug("ActivityLogRepository Activity log updated")
        return result

    async def delete(self, id: PydanticObjectId):
        """Delete an activity log entry"""
        _log.debug(f"ActivityLogRepository Deleting activity log: {id}")
        
        result = await ActivityLog.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Activity log not found: {id}")

        await result.delete()
        _log.debug("ActivityLogRepository Activity log deleted")
