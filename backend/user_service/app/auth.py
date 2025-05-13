from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from functools import lru_cache
import time

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Auth service configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
TOKEN_VALIDATION_ENDPOINT = f"{AUTH_SERVICE_URL}/api/auth/validate"

# Security scheme
security = HTTPBearer(auto_error=False)

# Models
class UserData(BaseModel):
    id: str
    username: str
    email: str
    role: str


# Cache configuration
TOKEN_CACHE_SIZE = int(os.getenv("TOKEN_CACHE_SIZE", "1024"))
TOKEN_CACHE_TTL = int(os.getenv("TOKEN_CACHE_TTL", "300"))  # 5 minutes in seconds


class AuthMiddleware:
    """Auth middleware to handle token validation and user extraction."""
    
    def __init__(self):
        self.client = None
        self._cache = {}
    
    async def get_http_client(self):
        """Get or create HTTP client with connection pooling."""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                timeout=5.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self.client
    
    async def close(self):
        """Close HTTP client."""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
    
    async def validate_token_cached(self, token: str) -> Dict[str, Any]:
        """Validate JWT token with caching."""
        try:
            # This is just the caching wrapper - actual validation happens in validate_token
            return await self.validate_token(token)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate token with proper error handling"""
        if not token:
            raise HTTPException(401, "Missing token")
            
        # Check cache first
        if token in self._cache:
            return self._cache[token]
            
        try:
            client = await self.get_http_client()
            response = await client.get(
                TOKEN_VALIDATION_ENDPOINT,
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                self._cache[token] = data  # Cache valid tokens
                return data
                
            raise HTTPException(response.status_code, "Invalid token")
            
        except httpx.RequestError as e:
            logger.error(f"Auth service error: {str(e)}")
            raise HTTPException(503, "Auth service unavailable")


# Create singleton instance
auth_middleware = AuthMiddleware()


# Helper functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> UserData:
    """Dependency to get the current authenticated user."""
    try:
        token = credentials.credentials
        user_data = await auth_middleware.validate_token_cached(token)
        
        # Convert user data to UserData model
        return UserData(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[UserData]:
    """Dependency to get the current user if authenticated, None otherwise."""
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        user_data = await auth_middleware.validate_token_cached(token)
        
        # Convert user data to UserData model
        return UserData(**user_data)
        
    except Exception as e:
        logger.warning(f"Optional user auth failed: {e}")
        return None


def get_admin_user(
    current_user: UserData = Depends(get_current_user)
) -> UserData:
    """Dependency to ensure the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user