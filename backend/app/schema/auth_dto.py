from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schema.base_dto import BaseModelJsonSerializable


class GoogleAuthRequest(BaseModelJsonSerializable):
    """Request model for Google OAuth2 authentication"""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModelJsonSerializable):
    """Response model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class GoogleUserProfile(BaseModelJsonSerializable):
    """User profile information from Google OAuth2"""
    id: str
    email: EmailStr
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = False


class AuthUserResponse(BaseModelJsonSerializable):
    """Authenticated user information response"""
    id: str
    email: EmailStr
    name: str
    role: str
    picture: Optional[str] = None
    is_active: bool
    auth_provider: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class LoginResponse(BaseModelJsonSerializable):
    """Response model for successful login"""
    user: AuthUserResponse
    token: TokenResponse


class RefreshTokenRequest(BaseModelJsonSerializable):
    """Request model for refreshing access token"""
    refresh_token: str


class GoogleLoginResponse(BaseModelJsonSerializable):
    """Response model for Google OAuth2 login URL"""
    auth_url: str
    message: str
    expires_in: Optional[int] = None
    state: Optional[str] = None


class LogoutResponse(BaseModelJsonSerializable):
    """Response model for user logout"""
    message: str
    user_id: str
    email: str
    logged_out_at: datetime
