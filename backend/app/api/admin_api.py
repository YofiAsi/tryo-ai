import logging
from typing import Annotated
import uuid

from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Request,
    status,
    Query
)
from fastapi.responses import JSONResponse

from app.conf.app_settings import server_settings
from app.schema.paging import PagingDTO
from app.schema.user_dto import UserDTO, CreateUserDTO, ChangeUserActiveStatusDTO
from app.schema.tasks_dto import  CreateTaskDTO, TaskWithDataDTO, BaseTaskDTO
from app.schema.activity_log_dto import (
    CreateActivityLogDTO,
    UpdateActivityLogDTO,
    ActivityLogDTO,
    ActivityLogFilterDTO,
    ActivityLogSummaryDTO
)
from app.api.api_response import response_fail_status_codes
from app.service.user_service import UserService
from app.service.task_service import TaskService
from app.service.activity_log_service import ActivityLogService
from app.conf.dependencies import get_user_service, get_task_service, get_activity_log_service
from app.utils.header_utils import create_list_header
from app.errors.business_exception import BusinessException
from app.conf.page_response import PageResponse

_resource = "admin"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
                   # dependencies=[Depends(auth_handler.get_token_user)],
                   responses=response_fail_status_codes
                   )


@router.get(
    path="/users",
    operation_id="get_users",
    name="get_users",
    summary="Get Users",
    response_model=list[UserDTO],
    status_code=status.HTTP_200_OK
)
async def get_users(
        request: Request, query: PagingDTO = Depends(PagingDTO),
        user_service: UserService = Depends(get_user_service)) -> UserDTO | None:
    _log.debug(f"BEGIN:get_users rest request")
    page_response = await user_service.find(None, query.page, query.size, "_id")
    _log.debug(f"AdminApi get_users rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [user.to_json() for user in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.post(
    path="/users",
    operation_id="create_user",
    name="create_user",
    summary="Create User",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        request: Request,
        user_data: CreateUserDTO = Body(...),
        user_service: UserService = Depends(get_user_service)) -> JSONResponse:
    _log.debug(f"BEGIN:create_user rest request")
    created_user = await user_service.create(
        user=user_data
    )
    _log.debug(f"AdminApi create_user rest response: {created_user}")
    
    return JSONResponse(
        content=created_user.to_json(),
        status_code=status.HTTP_201_CREATED
    )


@router.patch(
    path="/users/{user_id}/active-status",
    operation_id="change_user_active_status",
    name="change_user_active_status",
    summary="Change User Active Status",
    response_model=UserDTO,
    status_code=status.HTTP_200_OK
)
async def change_user_active_status(
        request: Request,
        user_id: PydanticObjectId,
        status_data: ChangeUserActiveStatusDTO = Body(...),
        user_service: UserService = Depends(get_user_service)) -> JSONResponse:
    _log.debug(f"BEGIN:change_user_active_status rest request for user: {user_id}")
    updated_user = await user_service.change_active_status(
        user_id=user_id,
        is_active=status_data.is_active
    )
    _log.debug(f"AdminApi change_user_active_status rest response: {updated_user}")
    
    return JSONResponse(
        content=updated_user.to_json(),
        status_code=status.HTTP_200_OK
    )


@router.get(
    path="/tasks",
    operation_id="get_tasks",
    name="get_tasks",
    summary="Get Tasks",
    response_model=list[BaseTaskDTO],
    status_code=status.HTTP_200_OK
)
async def get_tasks(
        request: Request, query: PagingDTO = Depends(PagingDTO),
        task_service: TaskService = Depends(get_task_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_tasks rest request")
    page_response = await task_service.find(None, query.page, query.size, "_id")
    _log.debug(f"AdminApi get_tasks rest response: {page_response}")

    headers = create_list_header(page_response)
    json_result = [BaseTaskDTO.model_validate(task).model_dump() for task in page_response.content]
    return JSONResponse(content=json_result, headers=headers)


@router.post(
    path="/tasks",
    operation_id="create_task",
    name="create_task",
    summary="Create Task",
    response_model=TaskWithDataDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
        request: Request,
        task_data: CreateTaskDTO = Body(...),
        task_service: TaskService = Depends(get_task_service)) -> JSONResponse:
    _log.debug(f"BEGIN:create_task rest request")
    
    if task_data.type.value == "cv_parsing":
        created_task = await task_service.create_cv_processing_task(task_data.data)
    else:
        raise ValueError(f"Unsupported task type: {task_data.type}")
    
    _log.debug(f"AdminApi create_task rest response: {created_task}")
    
    return JSONResponse(
        content=TaskWithDataDTO.model_validate(created_task).model_dump(),
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    path="/tasks/{task_id}",
    operation_id="get_task",
    name="get_task",
    summary="Get Task by ID",
    response_model=TaskWithDataDTO,
    status_code=status.HTTP_200_OK
)
async def get_task(
        request: Request,
        task_id: PydanticObjectId,
        task_service: TaskService = Depends(get_task_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_task rest request for task: {task_id}")
    task = await task_service.retrieve(task_id)
    if not task:
        return JSONResponse(
            content={"error": "Task not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    _log.debug(f"AdminApi get_task rest response: {task}")
    
    return JSONResponse(
        content=TaskWithDataDTO.model_validate(task).model_dump(),
        status_code=status.HTTP_200_OK
    )


@router.delete(
    path="/tasks/{task_id}",
    operation_id="delete_task",
    name="delete_task",
    summary="Delete Task",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
        request: Request,
        task_id: PydanticObjectId,
        task_service: TaskService = Depends(get_task_service)) -> JSONResponse:
    _log.debug(f"BEGIN:delete_task rest request for task: {task_id}")
    await task_service.delete(task_id)
    _log.debug(f"AdminApi delete_task rest response: Task deleted")
    
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    path="/tasks/{task_id}/status",
    operation_id="get_task_status",
    name="get_task_status",
    summary="Get Task Status and Progress",
    response_model=dict,
    status_code=status.HTTP_200_OK
)
async def get_task_status(
        request: Request,
        task_id: PydanticObjectId,
        task_service: TaskService = Depends(get_task_service)) -> JSONResponse:
    _log.debug(f"BEGIN:get_task_status rest request for task: {task_id}")
    
    try:
        task_status = {"status": "ABC"}
        _log.debug(f"AdminApi get_task_status rest response: {task_status}")
        
        return JSONResponse(
            content=task_status,
            status_code=status.HTTP_200_OK
        )
    except BusinessException as e:
        return JSONResponse(
            content={"error": e.msg, "code": e.code.name},
            status_code=status.HTTP_404_NOT_FOUND
        )


# Activity Log Endpoints
@router.get(
    path="/activity-logs",
    operation_id="get_activity_logs",
    name="get_activity_logs",
    summary="Get Activity Logs",
    response_model=list[ActivityLogDTO],
    status_code=status.HTTP_200_OK
)
async def get_activity_logs(
    request: Request,
    user_id: PydanticObjectId = Query(None, description="Filter by user ID"),
    activity_type: str = Query(None, description="Filter by activity type"),
    start_date: str = Query(None, description="Filter activities from this date (ISO format)"),
    end_date: str = Query(None, description="Filter activities until this date (ISO format)"),
    ip_address: str = Query(None, description="Filter by IP address"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Get activity logs with optional filtering and pagination.
    Admin access required.
    """
    _log.debug(f"BEGIN:get_activity_logs rest request")
    
    try:
        # Parse dates if provided
        from datetime import datetime
        start_date_obj = datetime.fromisoformat(start_date) if start_date else None
        end_date_obj = datetime.fromisoformat(end_date) if end_date else None
        
        # Parse activity type if provided
        from app.entity.activity_log_entity import ActivityType
        activity_type_obj = ActivityType(activity_type) if activity_type else None
        
        # Get filtered activity logs
        page_response = await activity_log_service.find_with_filters(
            user_id=user_id,
            activity_type=activity_type_obj,
            start_date=start_date_obj,
            end_date=end_date_obj,
            ip_address=ip_address,
            page=page,
            size=size
        )
        
        headers = create_list_header(page_response)
        json_result = [activity_log.to_json() for activity_log in page_response.content]
        _log.debug(f"AdminApi get_activity_logs rest response: {len(page_response.content)} logs")
        return JSONResponse(content=json_result, headers=headers)
        
    except Exception as e:
        _log.error(f"Error getting activity logs: {e}")
        return JSONResponse(
            content={"error": "Failed to retrieve activity logs"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    path="/activity-logs/{activity_log_id}",
    operation_id="get_activity_log",
    name="get_activity_log",
    summary="Get Activity Log by ID",
    response_model=ActivityLogDTO,
    status_code=status.HTTP_200_OK
)
async def get_activity_log(
    request: Request,
    activity_log_id: PydanticObjectId,
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Get a specific activity log by ID.
    Admin access required.
    """
    _log.debug(f"BEGIN:get_activity_log rest request for activity log: {activity_log_id}")
    
    try:
        activity_log = await activity_log_service.retrieve(activity_log_id)
        if not activity_log:
            return JSONResponse(
                content={"error": "Activity log not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        _log.debug(f"AdminApi get_activity_log rest response: {activity_log}")
        return JSONResponse(content=activity_log.to_json())
        
    except Exception as e:
        _log.error(f"Error getting activity log {activity_log_id}: {e}")
        return JSONResponse(
            content={"error": "Failed to retrieve activity log"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    path="/activity-logs/user/{user_id}",
    operation_id="get_user_activity_logs",
    name="get_user_activity_logs",
    summary="Get User Activity Logs",
    response_model=list[ActivityLogDTO],
    status_code=status.HTTP_200_OK
)
async def get_user_activity_logs(
    request: Request,
    user_id: PydanticObjectId,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Get activity logs for a specific user with pagination.
    Admin access required.
    """
    _log.debug(f"BEGIN:get_user_activity_logs rest request for user: {user_id}")
    
    try:
        page_response = await activity_log_service.find_by_user(
            user_id=user_id,
            page=page,
            size=size
        )
        
        _log.debug(f"AdminApi get_user_activity_logs rest response: {len(page_response.content)} logs")
        return JSONResponse(content=page_response.to_json())
        
    except Exception as e:
        _log.error(f"Error getting user activity logs for user {user_id}: {e}")
        return JSONResponse(
            content={"error": "Failed to retrieve user activity logs"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    path="/activity-logs/summary/statistics",
    operation_id="get_activity_summary",
    name="get_activity_summary",
    summary="Get Activity Summary Statistics",
    response_model=ActivityLogSummaryDTO,
    status_code=status.HTTP_200_OK
)
async def get_activity_summary(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Get summary statistics for activities in the last N days.
    Admin access required.
    """
    _log.debug(f"BEGIN:get_activity_summary rest request for last {days} days")
    
    try:
        summary = await activity_log_service.get_activity_summary(days)
        
        _log.debug(f"AdminApi get_activity_summary rest response: {summary.total_activities} total activities")
        return JSONResponse(content=summary.to_json())
        
    except Exception as e:
        _log.error(f"Error getting activity summary: {e}")
        return JSONResponse(
            content={"error": "Failed to retrieve activity summary"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    path="/activity-logs",
    operation_id="create_activity_log",
    name="create_activity_log",
    summary="Create Activity Log",
    response_model=ActivityLogDTO,
    status_code=status.HTTP_201_CREATED
)
async def create_activity_log(
    request: Request,
    activity_log_data: CreateActivityLogDTO = Body(...),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Create a new activity log entry.
    Admin access required.
    """
    _log.debug(f"BEGIN:create_activity_log rest request")
    
    try:
        # Create activity log
        created_activity_log = await activity_log_service.create(activity_log_data)
        
        _log.debug(f"AdminApi create_activity_log rest response: {created_activity_log}")
        return JSONResponse(
            content=created_activity_log.to_json(),
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        _log.error(f"Error creating activity log: {e}")
        return JSONResponse(
            content={"error": "Failed to create activity log"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put(
    path="/activity-logs/{activity_log_id}",
    operation_id="update_activity_log",
    name="update_activity_log",
    summary="Update Activity Log",
    response_model=ActivityLogDTO,
    status_code=status.HTTP_200_OK
)
async def update_activity_log(
    request: Request,
    activity_log_id: PydanticObjectId,
    update_data: UpdateActivityLogDTO = Body(...),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Update an existing activity log entry.
    Admin access required.
    """
    _log.debug(f"BEGIN:update_activity_log rest request for activity log: {activity_log_id}")
    
    try:
        updated_activity_log = await activity_log_service.update(
            activity_log_id,
            update_data
        )
        
        if not updated_activity_log:
            return JSONResponse(
                content={"error": "Activity log not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        _log.debug(f"AdminApi update_activity_log rest response: {updated_activity_log}")
        return JSONResponse(content=updated_activity_log.to_json())
        
    except Exception as e:
        _log.error(f"Error updating activity log {activity_log_id}: {e}")
        return JSONResponse(
            content={"error": "Failed to update activity log"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete(
    path="/activity-logs/{activity_log_id}",
    operation_id="delete_activity_log",
    name="delete_activity_log",
    summary="Delete Activity Log",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_activity_log(
    request: Request,
    activity_log_id: PydanticObjectId,
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Delete an activity log entry.
    Admin access required.
    """
    _log.debug(f"BEGIN:delete_activity_log rest request for activity log: {activity_log_id}")
    
    try:
        await activity_log_service.delete(activity_log_id)
        
        _log.debug(f"AdminApi delete_activity_log rest response: deleted")
        return JSONResponse(
            content=None,
            status_code=status.HTTP_204_NO_CONTENT
        )
        
    except Exception as e:
        _log.error(f"Error deleting activity log {activity_log_id}: {e}")
        return JSONResponse(
            content={"error": "Failed to delete activity log"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    path="/activity-logs/cleanup/old-logs",
    operation_id="cleanup_old_logs",
    name="cleanup_old_logs",
    summary="Clean Up Old Activity Logs",
    status_code=status.HTTP_200_OK
)
async def cleanup_old_logs(
    request: Request,
    days: int = Query(90, ge=30, le=365, description="Delete logs older than this many days"),
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
) -> JSONResponse:
    """
    Clean up old activity logs (for data maintenance).
    Admin access required.
    """
    _log.debug(f"BEGIN:cleanup_old_logs rest request for logs older than {days} days")
    
    try:
        deleted_count = await activity_log_service.cleanup_old_logs(days)
        
        _log.debug(f"AdminApi cleanup_old_logs rest response: {deleted_count} logs deleted")
        return JSONResponse(
            content={
                "message": f"Successfully cleaned up {deleted_count} old activity logs",
                "deleted_count": deleted_count
            }
        )
        
    except Exception as e:
        _log.error(f"Error cleaning up old logs: {e}")
        return JSONResponse(
            content={"error": "Failed to clean up old logs"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


