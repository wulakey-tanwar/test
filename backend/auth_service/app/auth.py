from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .database import get_user_by_id
from .models import TokenData
import logging

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

logger = logging.getLogger("auth-service.auth")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(user_data: dict):
    """Create JWT with complete user information"""
    to_encode = {
        "user_id": str(user_data["_id"]),
        "username": user_data["username"],
        "email": user_data["email"],
        "role": user_data.get("role", "user")
    }
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Security(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            logger.warning("Token missing user_id")
            raise credentials_exception
            
        user = await get_user_by_id(user_id)
        if user is None:
            logger.warning(f"User not found for ID: {user_id}")
            raise credentials_exception
            
        if not user.get("is_active", True):
            logger.warning(f"Inactive user attempted access: {user_id}")
            raise credentials_exception
            
        return {
            "_id": user["_id"],
            "username": user["username"],
            "email": user["email"],
            "role": payload.get("role", "user")
        }
        
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise credentials_exception