from fastapi import APIRouter

from .admin_api import router as admin_router
from .candidates_api import router as candidates_router
from .job_positions_api import router as job_positions_router
from .ai_agents_api import router as ai_agents_router
from .llm_api import router as llm_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(candidates_router)
api_router.include_router(job_positions_router)
api_router.include_router(ai_agents_router)
api_router.include_router(llm_router)

__all__ = ["admin_router", "candidates_router", "job_positions_router", "ai_agents_router", "llm_router", "api_router"]
