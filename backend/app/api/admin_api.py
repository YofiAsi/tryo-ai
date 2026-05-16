import logging

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
from app.api.api_response import response_fail_status_codes
from app.service.user_service import UserService
from app.service.task_service import TaskService
from app.conf.dependencies import get_user_service, get_task_service
from app.utils.header_utils import create_list_header
from app.errors.business_exception import BusinessException
from app.conf.page_response import PageResponse

_resource = "admin"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
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

