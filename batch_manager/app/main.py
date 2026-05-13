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
        from app.conf.database import close_db_connection, init_db
        await init_db()
        _log.info("Database initialized successfully")
    except Exception as e:
        _log.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Initialize OpenAI clients
    try:
        from app.conf.dependencies import get_multi_key_openai_client
        openai_client_service = get_multi_key_openai_client()
        await openai_client_service.init_clients()
        _log.info("OpenAI clients initialized successfully")
    except Exception as e:
        _log.error(f"Failed to initialize OpenAI clients: {str(e)}")
        raise
    
    # Initialize and start batch download queue service
    batch_download_queue = None
    try:
        from app.conf.dependencies import get_batch_download_queue_service
        batch_download_queue = await get_batch_download_queue_service()
        await batch_download_queue.start()
        _log.info("Batch download queue service started successfully")
    except Exception as e:
        _log.error(f"Failed to start batch download queue service: {str(e)}")
        # Don't raise here to allow the app to start even if queue fails
        # This provides graceful degradation
    
    # Initialize and start batch scheduler
    batch_scheduler = None
    try:
        from app.conf.dependencies import get_batch_scheduler_service
        batch_scheduler = get_batch_scheduler_service()
        await batch_scheduler.start()
        _log.info("Batch scheduler started successfully")
    except Exception as e:
        _log.error(f"Failed to start batch scheduler: {str(e)}")
        # Don't raise here to allow the app to start even if scheduler fails
        # This provides graceful degradation
    
    yield
    
    # Cleanup on shutdown
    try:
        if batch_download_queue and batch_download_queue.is_running:
            await batch_download_queue.stop()
            _log.info("Batch download queue service stopped")
    except Exception as e:
        _log.error(f"Error stopping batch download queue service: {str(e)}")
    
    try:
        if batch_scheduler and batch_scheduler.is_running:
            await batch_scheduler.stop()
            _log.info("Batch scheduler stopped")
    except Exception as e:
        _log.error(f"Error stopping batch scheduler: {str(e)}")
    
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
