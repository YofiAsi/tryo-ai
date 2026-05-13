import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.conf.app_settings import app_settings, server_settings, cors_settings
from app.conf.env.db_config import init_db
from app.conf.env.sentry_config import init_sentry, is_sentry_enabled
from app.errors.business_exception import BusinessException
from app.migration.user_migration import init_migration


_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(_):
    _log.debug("FastAPI Lifespan started")
    
    # Initialize Sentry
    await init_sentry()
    
    await init_db()
    await init_migration()
    yield


tags_metadata = [
    {
        "name": "auth",
        "description": "Operations with authentication. The **login** endpoint returns the access token."
    },
    {
        "name": "account",
        "description": "Operations with account. The **account** endpoint returns the account information."
    },
    {
        "name": "users",
        "description": "Operations with users. The **users** endpoint returns the user information."
    },
    {
        "name": "candidates",
        "description": "Operations with candidates. The **candidates** endpoint returns the candidate information."
    },
    {
        "name": "job-positions",
        "description": "Operations with job positions. The **job-positions** endpoint returns the job position information."
    },
    {
        "name": "admin",
        "description": "Administrative operations for managing users, tasks, and system resources."
    },
    {
        "name": "ai-agents",
        "description": "AI-powered operations including job position analysis, candidate screening, and intelligent insights."
    }
]
app = FastAPI(
    title=app_settings.APP_NAME,
    summary=app_settings.APP_DESCRIPTION,
    description=app_settings.APP_DESCRIPTION,
    version="1.0.0",
    docs_url=f"{server_settings.CONTEXT_PATH}/docs",
    redoc_url=f"{server_settings.CONTEXT_PATH}/redoc",
    openapi_url=f"{server_settings.CONTEXT_PATH}/openapi.json",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    contact={
        "name": f"{app_settings.APP_NAME} Team",
        "url": "https://github.com/cevheri",
        "email": "cevheribozoglan@gmail.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://github.com/cevheri/pyfapi/blob/main/LICENSE"
    },
    terms_of_service="https://example.com/terms/"
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.ALLOWED_ORIGINS,
    allow_credentials=cors_settings.ALLOW_CREDENTIALS,
    allow_methods=cors_settings.ALLOWED_METHODS,
    allow_headers=cors_settings.ALLOWED_HEADERS,
    expose_headers=['X-Total-Count', 'X-Page', 'X-Size']
)

app.include_router(api_router)

def write_log(request: Request, exc: BusinessException):
    _log.error(f"BusinessException - Request: {request.method} {request.url.path} failed with {exc.code} {exc.msg}")


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    # Capture business exceptions in Sentry if enabled
    if is_sentry_enabled():
        from app.utils.sentry_utils import capture_exception, set_context, set_tag
        
        # Set context for better error tracking
        set_context("request", {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers)
        })
        
        # Set tags for easier filtering
        set_tag("error_type", "business_exception")
        set_tag("error_code", exc.code.name)
        set_tag("http_status", str(status.HTTP_400_BAD_REQUEST))
        
        # Capture the exception
        capture_exception(exc, {
            "business_error_code": exc.code.name,
            "business_error_message": exc.msg
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": {"error_code": f"{status.HTTP_400_BAD_REQUEST}.{exc.code.name}", "error_message": exc.msg}},
        headers={"X-Error": f"{status.HTTP_400_BAD_REQUEST}.{exc.code}"},
        media_type="application/json",
        background=write_log(request, exc),
    )


@app.get("/api/v1/health")
async def health():
    return {"status": "UP"}

@app.get("/api/v1/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0