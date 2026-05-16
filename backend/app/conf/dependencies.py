from fastapi import Depends

from app.repository.user_repository import UserRepository
from app.service.user_service import UserService
from app.repository.candidate_repository import CandidateRepository
from app.service.candidate_service import CandidateService
from app.repository.task_repository import TaskRepository
from app.service.task_service import TaskService
from app.repository.job_position_repository import JobPositionRepository
from app.service.job_position_service import JobPositionService
from app.service.ai_agents_service import AIAgentsService


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


async def get_ai_agents_service() -> AIAgentsService:
    return AIAgentsService()
