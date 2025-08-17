from fastapi import APIRouter

from .admin_api import router as admin_router
from .candidates_api import router as candidates_router
from .auth_api import router as auth_router
from .job_positions_api import router as job_positions_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(candidates_router)
api_router.include_router(auth_router)
api_router.include_router(job_positions_router)

__all__ = ["admin_router", "candidates_router", "auth_router", "job_positions_router", "api_router"]
