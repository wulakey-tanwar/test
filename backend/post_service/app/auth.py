from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import httpx
import os
from typing import Dict, Optional

security = HTTPBearer()

class Auth:
    """Authentication middleware to validate JWT tokens and user access"""
    
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:8000")
    USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://user-service:8001")
    JWT_SECRET = os.environ.get("JWT_SECRET")  # For local token validation
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    
    @classmethod
    async def get_current_user(cls, credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
        """
        Validate JWT token and return current user
        """
        token = credentials.credentials

        try:
            # Local validation for quick checks
            payload = jwt.decode(token, cls.JWT_SECRET, algorithms=[cls.JWT_ALGORITHM])
            user_id = payload.get("user_id")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

        # For more thorough validation, call auth service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.AUTH_SERVICE_URL}/api/auth/validate",  # ✅ fixed path
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code != 200:
                    print("Auth service response:", response.text)  # 🔍 debug output
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed",
                    )

                user_data = response.json()
                return user_data

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    
    @classmethod
    async def get_user_info(cls, user_id: str, token: str) -> Dict:
        """
        Get user information from the user service
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.USER_SERVICE_URL}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            return response.json()
    
    @classmethod
    async def get_following_ids(cls, user_id: str, token: str) -> list:
        """
        Get list of user IDs that the current user is following
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.USER_SERVICE_URL}/users/{user_id}/following",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                return []
            
            following_data = response.json()
            return [user["id"] for user in following_data]

    @classmethod
    async def verify_post_ownership(cls, user_id: str, post_author_id: str) -> bool:
        """
        Verify that the user owns the post
        """
        return user_id == post_author_id