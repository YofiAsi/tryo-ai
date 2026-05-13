from fastapi import APIRouter

from .manager_api import router as manager_router

api_router = APIRouter()
api_router.include_router(manager_router)

__all__ = ["api_router"]
