import logging
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.errors.business_exception import BusinessException

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    _log.debug("FastAPI Batch Manager Lifespan started")
    
    # Initialize database connection
    try:
        from app.conf.database import init_db, close_db_connection
        await init_db()
        _log.info("Database initialized successfully")
    except Exception as e:
        _log.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Cleanup on shutdown
    try:
        await close_db_connection()
        _log.info("Database connections closed")
    except Exception as e:
        _log.error(f"Error during database cleanup: {str(e)}")


tags_metadata = [
    {
        "name": "batch-manager",
        "description": "Operations with OpenAI batches. Create, monitor, and retrieve batch processing results."
    }
]

app = FastAPI(
    title="Tyro Batch Manager API",
    summary="OpenAI Batch Processing Management Service",
    description="Service for creating and managing OpenAI Batch API operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['X-Total-Count', 'X-Page', 'X-Size']
)

app.include_router(api_router)


def write_log(request: Request, exc: BusinessException) -> None:
    _log.error(f"BusinessException - Request: {request.method} {request.url.path} failed with {exc.code} {exc.msg}")


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    write_log(request, exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": {"error_code": f"{status.HTTP_400_BAD_REQUEST}.{exc.code.name}", "error_message": exc.msg}},
        headers={"X-Error": f"{status.HTTP_400_BAD_REQUEST}.{exc.code}"},
        media_type="application/json",
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    exc_str = str(exc)
    exc_type = type(exc).__name__
    
    # Log the full exception with traceback
    _log.error(f"Global Exception Handler - {exc_type}: {exc_str}")
    _log.error(f"Request: {request.method} {request.url}")
    _log.error(f"Full traceback:\n{traceback.format_exc()}")
    
    # Print to console for immediate visibility
    print(f"🚨 UNHANDLED EXCEPTION: {exc_type}: {exc_str}")
    print(f"🔍 Request: {request.method} {request.url}")
    print(f"📍 Full traceback:\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "error_type": exc_type,
                "error_message": exc_str,
                "request_method": request.method,
                "request_url": str(request.url)
            }
        }
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP", "service": "batch-manager"}
