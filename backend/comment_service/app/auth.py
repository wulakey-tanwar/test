from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
import httpx
import os
from typing import Dict, Optional
import logging
from dotenv import load_dotenv
import jwt
from jwt.exceptions import PyJWTError
import time
from functools import lru_cache

# Load environment variables
load_dotenv()

logger = logging.getLogger("comment-service.auth")

# Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# Cache token verification results for 60 seconds to reduce load on auth service
TOKEN_CACHE_TTL = int(os.getenv("TOKEN_CACHE_TTL", "60"))

security = HTTPBearer()


class TokenVerifier:
    def __init__(self):
        self.auth_service_url = AUTH_SERVICE_URL
        self.user_service_url = USER_SERVICE_URL
        
    async def verify_token(self, token: str) -> Dict:
        """Verify JWT token with the auth service or locally if JWT_SECRET is provided"""
        try:
            # If JWT_SECRET is provided, verify locally to reduce network calls
            if JWT_SECRET:
                return self._verify_token_locally(token)
            else:
                return await self._verify_token_with_service(token)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def _verify_token_locally(self, token: str) -> Dict:
        """Verify JWT token locally using the secret key"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check if token is expired
            if payload.get("exp") and payload["exp"] < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return payload
        except PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @lru_cache(maxsize=100)
    async def _verify_token_with_service(self, token: str) -> Dict:
        """Verify JWT token with the auth service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/verify",
                    json={"token": token},
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                    
                return response.json()
        except httpx.RequestError:
            logger.error("Error connecting to auth service")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is unavailable",
            )
    
    async def get_user_info(self, user_id: str) -> Dict:
        """Get user information from the user service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}",
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )
                    
                return response.json()
        except httpx.RequestError:
            logger.error("Error connecting to user service")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service is unavailable",
            )


# Create a single instance for reuse
token_verifier = TokenVerifier()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Dependency for getting the current authenticated user"""
    token = credentials.credentials
    user_data = await token_verifier.verify_token(token)
    
    if not user_data or "user_id" not in user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user_data


def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict]:
    """Dependency for getting the current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    # Use the synchronous event loop to call the async function
    import asyncio
    try:
        return asyncio.run(get_current_user(credentials))
    except HTTPException:
        return None


async def verify_post_exists(post_id: str) -> bool:
    """Verify that a post exists in the post service"""
    post_service_url = os.getenv("POST_SERVICE_URL", "http://post-service:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{post_service_url}/api/v1/posts/{post_id}/exists",
                timeout=5.0
            )
            
            return response.status_code == 200
    except httpx.RequestError:
        logger.error("Error connecting to post service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Post service is unavailable",
        )