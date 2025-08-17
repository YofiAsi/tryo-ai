import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from urllib.parse import urlencode

from fastapi import HTTPException, status
from jose import JWTError, jwt
from starlette.requests import Request

from app.conf.env.oauth_config import oauth2_settings
from app.consts import UserRole
from app.entity.user_entity import User
from app.entity.activity_log_entity import ActivityType
from app.schema.auth_dto import GoogleUserProfile, TokenResponse, AuthUserResponse, LoginResponse

_log = logging.getLogger(__name__)


class AuthService:
    """Authentication service for handling OAuth2 and JWT operations"""
    
    def __init__(self, activity_log_service=None):
        self.activity_log_service = activity_log_service
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=oauth2_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, oauth2_settings.JWT_SECRET_KEY, algorithm=oauth2_settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, oauth2_settings.JWT_SECRET_KEY, algorithms=[oauth2_settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_google_user(self, request: Request, code: str) -> LoginResponse:
        """Authenticate user with Google OAuth2 code"""
        try:
            # Exchange authorization code for access token
            token_data = await self._exchange_code_for_token(code)
            
            # Get user info from Google using the access token
            google_profile = await self._get_google_user_info(token_data['access_token'])
            
            # Find existing user (no new user creation allowed)
            user = await self._get_existing_user(google_profile)
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            await user.save()
            
            # Log login activity
            await self._log_login_activity(user, request)
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role.value}
            )
            
            # Create token response
            token_response = TokenResponse(
                access_token=access_token,
                expires_in=oauth2_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            # Create user response
            user_response = AuthUserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
                role=user.role.value,
                picture=user.picture,
                is_active=user.is_active,
                auth_provider=user.auth_provider,
                created_at=user.created_at or datetime.now(timezone.utc),
                updated_at=user.updated_at or datetime.now(timezone.utc),
                last_login=user.last_login
            )
            
            return LoginResponse(user=user_response, token=token_response)
            
        except Exception as e:
            _log.error(f"Google authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google authentication failed"
            )
    
    async def _get_existing_user(self, google_profile: GoogleUserProfile) -> User:
        """Get existing user from Google profile - no new user creation allowed"""
        # Try to find user by Google ID first
        _log.info(f"Getting existing user from Google profile: {google_profile}")   
        user = await User.find_one({"google_id": google_profile.id})
        
        if user:
            return user
        
        # Try to find user by email
        user = await User.find_one({"email": google_profile.email})
        
        if user:
            # Update existing user with Google info
            user.google_id = google_profile.id
            user.auth_provider = "google"
            user.picture = google_profile.picture
            user.name = google_profile.name
            await user.save()
            return user
        
        # User not found - throw error (no new user creation allowed)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Google account {google_profile.email} is not authorized to access this system. Please contact your administrator to create an account first."
        )
    
    async def _exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': oauth2_settings.GOOGLE_CLIENT_ID,
            'client_secret': oauth2_settings.GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': oauth2_settings.GOOGLE_REDIRECT_URI
        }
        
        _log.info(f"Exchanging code for token: {data}")
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                error_text = response.text
                _log.error(f"Token exchange failed: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code for token"
                )
            
            token_data = response.json()
            return token_data
    
    async def _get_google_user_info(self, access_token: str) -> GoogleUserProfile:
        """Get user information from Google using access token"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            if response.status_code != 200:
                error_text = response.text
                _log.error(f"Failed to get user info: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user information from Google"
                )
            
            user_data = response.json()
            return GoogleUserProfile(**user_data)
    
    def get_google_auth_url(self) -> str:
        """Get Google OAuth2 authorization URL"""
        params = {
            'client_id': oauth2_settings.GOOGLE_CLIENT_ID,
            'redirect_uri': oauth2_settings.GOOGLE_REDIRECT_URI,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await User.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    
    async def _log_login_activity(self, user: User, request: Request):
        """Log user login activity"""
        if not self.activity_log_service:
            _log.warning("Activity log service not available, skipping login logging")
            return
        
        try:
            # Extract client information from request
            client_host = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Log the login activity
            await self.activity_log_service.log_user_activity(
                user=user,
                activity_type=ActivityType.LOGIN,
                data={
                    "login_method": "google_oauth",
                    "success": True,
                    "auth_provider": user.auth_provider
                },
                ip_address=client_host,
                user_agent=user_agent
            )
            
            _log.debug(f"Login activity logged for user: {user.email}")
            
        except Exception as e:
            _log.error(f"Failed to log login activity for user {user.email}: {e}")
            # Don't fail the login if activity logging fails


# Global instance
auth_service = AuthService()
