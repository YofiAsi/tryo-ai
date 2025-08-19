import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.errors.business_exception import BusinessException

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(_):
    _log.debug("FastAPI Batch Manager Lifespan started")
    # TODO: Initialize database connection
    # await init_db()
    yield


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


def write_log(request: Request, exc: BusinessException):
    _log.error(f"BusinessException - Request: {request.method} {request.url.path} failed with {exc.code} {exc.msg}")


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": {"error_code": f"{status.HTTP_400_BAD_REQUEST}.{exc.code.name}", "error_message": exc.msg}},
        headers={"X-Error": f"{status.HTTP_400_BAD_REQUEST}.{exc.code}"},
        media_type="application/json",
        background=write_log(request, exc),
    )


@app.get("/health")
async def health():
    return {"status": "UP", "service": "batch-manager"}
