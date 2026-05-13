import os
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.repository.user_repository import UserRepository
from app.service.user_service import UserService
from app.repository.candidate_repository import CandidateRepository
from app.service.candidate_service import CandidateService
from app.repository.task_repository import TaskRepository
from app.service.task_service import TaskService
from app.repository.job_position_repository import JobPositionRepository
from app.service.job_position_service import JobPositionService
from app.repository.activity_log_repository import ActivityLogRepository
from app.service.activity_log_service import ActivityLogService
from app.service.ai_agents_service import AIAgentsService
from app.service.auth_service import auth_service
from app.entity.user_entity import User
from app.consts import UserRole
from app.conf.app_settings import openai_settings

DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"
DEV_USER_EMAIL = "dev@local.dev"

security = HTTPBearer(auto_error=not DEV_AUTH_BYPASS)


async def _get_or_create_dev_user() -> User:
    user = await User.find_one(User.email == DEV_USER_EMAIL)
    if user is None:
        now = datetime.now(timezone.utc)
        user = User(
            name="Dev User",
            email=DEV_USER_EMAIL,
            role=UserRole.ADMIN,
            is_active=True,
            auth_provider="dev",
            created_at=now,
            updated_at=now,
        )
        await User.create(user)
    return user


async def get_user_repository() -> UserRepository:
    return UserRepository()


async def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)


async def get_candidate_repository() -> CandidateRepository:
    return CandidateRepository()


async def get_candidate_service(candidate_repository: CandidateRepository = Depends(get_candidate_repository)) -> CandidateService:
    return CandidateService(candidate_repository)


async def get_task_repository() -> TaskRepository:
    return TaskRepository()


async def get_task_service(task_repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(task_repository)


async def get_job_position_repository() -> JobPositionRepository:
    return JobPositionRepository()


async def get_job_position_service(job_position_repository: JobPositionRepository = Depends(get_job_position_repository)) -> JobPositionService:
    return JobPositionService(job_position_repository)


async def get_activity_log_repository() -> ActivityLogRepository:
    return ActivityLogRepository()


async def get_activity_log_service(
    activity_log_repository: ActivityLogRepository = Depends(get_activity_log_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> ActivityLogService:
    return ActivityLogService(activity_log_repository, user_repository)


async def get_auth_service(
    activity_log_service: ActivityLogService = Depends(get_activity_log_service)
):
    """Get auth service with activity logging enabled"""
    from app.service.auth_service import AuthService
    return AuthService(activity_log_service=activity_log_service)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user
    Use this in your API endpoints to require authentication
    """
    if DEV_AUTH_BYPASS:
        return await _get_or_create_dev_user()
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current authenticated and active user
    Use this when you need to ensure the user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current authenticated admin user
    Use this for admin-only endpoints
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_ai_agents_service() -> AIAgentsService:
    """
    Dependency to get AI Agents Service
    Use this for AI agent operations
    """
    return AIAgentsService()
