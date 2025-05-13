from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from bson.objectid import ObjectId
from typing import List, Optional
import logging
from datetime import datetime

from ..auth import get_current_user, get_admin_user, UserData, get_optional_user
from ..models import (
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfileResponse, 
    PaginatedResponse
)
from ..database import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
    get_users,
    check_follow_status
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Helper function to convert MongoDB user object to response model
def user_to_response(user, is_following=None) -> dict:
    if not user:
        return None
        
    # Ensure proper datetime serialization
    created_at = user["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
        
    return {
        "_id": str(user["_id"]),
        "username": user["username"],
        "full_name": user["full_name"],
        "bio": user.get("bio"),
        "avatar_url": user.get("avatar_url"),
        "location": user.get("location"),
        "website": user.get("website"),
        "created_at": created_at,
        "follower_count": user.get("follower_count", 0),
        "following_count": user.get("following_count", 0),
        "is_following": is_following if is_following is not None else None
    }
    
    # Add is_following field if provided
    if is_following is not None:
        response["is_following"] = is_following
        
    return response


@router.post(
    "",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user profile",
    description="Create a new user profile in the system.",
)
async def create_user_profile(
    profile: UserProfileCreate,
    current_user: UserData = Depends(get_current_user)
):
    """
    Create a new user profile (Authenticated users only).
    
    This endpoint allows logged-in users to create their profile.
    """
    # Check if username already exists
    existing_user = await get_user_by_username(profile.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Check if email already exists    
    existing_email = await get_user_by_email(profile.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Prepare user data
    user_data = profile.dict()
    now = datetime.utcnow()
    user_data.update({
        "_id": ObjectId(),  # ✅ Important: use ObjectId for MongoDB _id
        "created_at": now,
        "updated_at": now,
        "is_active": True,
        "follower_count": 0,
        "following_count": 0,
        "user_id": str(current_user.id)  # Optional: keep track of auth user
    })

    # Insert into DB
    new_user = await create_user(user_data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return user_to_response(new_user)

@router.get(
    "",
    response_model=PaginatedResponse,
    summary="Get all user profiles",
    description="Get a paginated list of all active user profiles.",
)
async def get_user_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[UserData] = Depends(get_optional_user)
):
    """
    Get a paginated list of all user profiles.
    
    This endpoint allows fetching all user profiles with pagination.
    """
    # Calculate skip based on page and limit
    skip = (page - 1) * limit
    
    # Get users with pagination
    result = await get_users(skip, limit)
    
    # Process users to add is_following field if user is authenticated
    if current_user:
        for user in result["data"]:
            is_following = await check_follow_status(current_user.id, str(user["_id"]))
            user["is_following"] = is_following
    
    return result


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user profile by ID",
    description="Get a user profile by its ID.",
)
async def get_user_profile_by_id(
    user_id: str = Path(..., description="The ID of the user"),
    current_user: Optional[UserData] = Depends(get_optional_user)
):
    """
    Get a user profile by ID.
    
    This endpoint allows fetching a specific user profile by ID.
    """
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user follows this user
    is_following = None
    if current_user:
        is_following = await check_follow_status(current_user.id, user_id)
    
    # Return user response
    return user_to_response(user, is_following)


@router.get(
    "/username/{username}",
    response_model=UserProfileResponse,
    summary="Get user profile by username",
    description="Get a user profile by username.",
)
async def get_user_profile_by_username(
    username: str = Path(..., description="The username of the user"),
    current_user: Optional[UserData] = Depends(get_optional_user)
):
    """
    Get a user profile by username.
    
    This endpoint allows fetching a specific user profile by username.
    """
    # Get user from database
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user follows this user
    is_following = None
    if current_user:
        is_following = await check_follow_status(current_user.id, str(user["_id"]))
    
    # Return user response
    return user_to_response(user, is_following)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user.",
)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    current_user: UserData = Depends(get_current_user)
):
    """
    Update current user profile.
    
    This endpoint allows a user to update their own profile.
    """
    # Get existing user
    user = await get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user in database
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    updated_user = await update_user(current_user.id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    # Return updated user
    return user_to_response(updated_user)


@router.put(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Update user profile by ID",
    description="Update a user profile by ID (Admin only).",
)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    user_id: str = Path(..., description="The ID of the user"),
    current_user: UserData = Depends(get_admin_user)
):
    """
    Update user profile (Admin only).
    
    This endpoint allows administrators to update any user profile.
    """
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Get existing user
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user in database
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    updated_user = await update_user(user_id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    # Return updated user
    return user_to_response(updated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user profile",
    description="Soft delete a user profile (Admin only).",
)
async def delete_user_profile(
    user_id: str = Path(..., description="The ID of the user"),
    current_user: UserData = Depends(get_admin_user)
):
    """
    Delete user profile (Admin only).
    
    This endpoint allows administrators to soft delete a user profile.
    """
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user (soft delete)
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    # Return no content
    return None