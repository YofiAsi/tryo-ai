import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.conf.app_settings import server_settings
from app.api.api_response import response_fail_status_codes

from app.conf.dependencies import get_auth_service, get_current_user as get_authenticated_user
from app.service.auth_service import AuthService

from app.schema.auth_dto import GoogleAuthRequest, LoginResponse, AuthUserResponse, GoogleLoginResponse, LogoutResponse
from app.entity.user_entity import User

_resource = "auth"
_path = f"{server_settings.CONTEXT_PATH}/{_resource}"
_log = logging.getLogger(__name__)

router = APIRouter(prefix=_path,
                   tags=[_resource],
                   # dependencies=[Depends(auth_handler.get_token_user)],
                   responses=response_fail_status_codes
                   )
security = HTTPBearer()


@router.get(
    "/google/login",
    response_model=GoogleLoginResponse,
    summary="Get Google OAuth2 Login URL",
    description="Retrieve the Google OAuth2 authentication URL for user login",
    response_description="Google OAuth2 authentication URL and instructions"
)
async def google_login(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get Google OAuth2 login URL
    
    Returns:
        GoogleLoginResponse: Contains the authentication URL and user instructions
        
    Example:
        The response will include:
        - auth_url: The Google OAuth2 URL to redirect users to
        - message: Instructions for the user
        - expires_in: Optional expiration time for the auth URL
        - state: Optional state parameter for security
    """
    auth_url = auth_service.get_google_auth_url()
    return GoogleLoginResponse(
        auth_url=auth_url,
        message="Redirect user to this URL to authenticate with Google",
        expires_in=3600,  # 1 hour default expiration
        state=None  # Could be generated for additional security
    )


@router.post(
    "/google/callback",
    response_model=LoginResponse,
    summary="Google OAuth2 Callback",
    description="Handle Google OAuth2 callback and authenticate user",
    response_description="User authentication result with access token"
)
async def google_callback(
    request: Request, 
    auth_request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handle Google OAuth2 callback and authenticate user
    
    This endpoint processes the authorization code returned by Google OAuth2
    and exchanges it for user information and authentication tokens.
    
    Args:
        request: FastAPI request object
        auth_request: Google OAuth2 authorization code and optional state
        
    Returns:
        LoginResponse: User information and authentication tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = await auth_service.authenticate_google_user(request, auth_request.code)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="Get Current User",
    description="Retrieve information about the currently authenticated user",
    response_description="Current user profile information"
)
async def get_current_user(
    user: User = Depends(get_authenticated_user),
):
    """
    Get current authenticated user information
    """
    return AuthUserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        picture=user.picture,
        is_active=user.is_active,
        auth_provider=user.auth_provider,
        created_at=user.created_at or user.created_at,
        updated_at=user.updated_at or user.updated_at,
        last_login=user.last_login
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout User",
    description="Logout user and invalidate authentication token",
    response_description="Logout confirmation with user details"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user (invalidate token)
    
    Note: In a stateless JWT system, tokens are invalidated client-side.
    This endpoint can be used for audit logging and user session tracking.
    
    Returns:
        LogoutResponse: Confirmation of successful logout with user details
        
    Raises:
        HTTPException: If authentication credentials are invalid
    """
    try:
        # Verify token to get user info for logging
        user = await auth_service.get_current_user(credentials.credentials)
        
        # In a real implementation, you might want to add the token to a blacklist
        # or implement refresh token rotation
        
        from datetime import datetime, timezone
        return LogoutResponse(
            message="Successfully logged out",
            user_id=str(user.id),
            email=user.email,
            logged_out_at=datetime.now(timezone.utc)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
