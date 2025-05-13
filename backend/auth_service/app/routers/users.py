from fastapi import APIRouter, HTTPException, status, Depends, Response
from pymongo.collection import Collection
from ..models import UserCreate, UserLogin, UserResponse, TokenResponse
from ..database import create_user, get_user_by_email, get_users_collection
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user
import logging

router = APIRouter(tags=["authentication"])

logger = logging.getLogger("auth-service.users")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, users_collection: Collection = Depends(get_users_collection)):
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email, users_collection)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # ✅ Check if username exists
    existing_username = await users_collection.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user with hashed password
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    
    try:
        new_user = await create_user(user_dict, users_collection)
        return {
            "id": str(new_user["_id"]),
            "email": new_user["email"],
            "full_name": new_user["full_name"],
            "username": new_user["username"]
        }
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, users_collection: Collection = Depends(get_users_collection)):
    # Find the user
    user = await get_user_by_email(user_credentials.email, users_collection)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate access token
    access_token = create_access_token(user_data=user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "username": user["username"]
        }
    }


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "username": current_user["username"]
    }