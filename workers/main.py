"""
Main FastAPI application for CV Parse Batch Task Service.

This module contains the FastAPI application initialization and configuration.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import debugpy  # type: ignore
from api.test_api import router as test_api_router
from fastapi import FastAPI

_log = logging.getLogger(__name__)

def setup_debugpy() -> None:
    """Setup debugpy for remote debugging."""
    # Check if debugpy is enabled via environment variable
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        debug_port = int(os.getenv("DEBUG_PORT", "5679"))
        debug_host = os.getenv("DEBUG_HOST", "0.0.0.0")
        
        print(f"Starting debugpy server on {debug_host}:{debug_port}")
        debugpy.listen((debug_host, debug_port))
        
        # Wait for debugger to attach if specified
        if os.getenv("WAIT_FOR_DEBUGGER", "false").lower() == "true":
            print("Waiting for debugger to attach...")
            debugpy.wait_for_client()
        else:
            print("Debugpy server started. Attach debugger when ready.")
    else:
        print("Debug mode disabled. Set DEBUG_MODE=true to enable debugging.")

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    _log.debug("FastAPI Workers Lifespan started")
    setup_debugpy()
    # Initialize database connection
    try:
        from common.conf.database import close_db_connection, init_db
        await init_db()
        _log.info("Database initialized successfully")
    except Exception as e:
        _log.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Cleanup on shutdown
    try:
        await close_db_connection()
        _log.info("Database connection closed")
    except Exception as e:
        _log.error(f"Error closing database connection: {str(e)}")


# Initialize FastAPI app
app = FastAPI(
    title="CV Parse Batch Task Service",
    description="Service for CV parsing batch tasks - Create tasks and process results",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Include routers
app.include_router(test_api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
