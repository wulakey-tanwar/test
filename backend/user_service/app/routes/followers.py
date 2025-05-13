from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from bson.objectid import ObjectId
from typing import List, Optional
import logging

from ..auth import get_current_user, UserData
from ..models import FollowRequest, FollowResponse, PaginatedResponse
from ..database import (
    get_user_by_id,
    follow_user,
    unfollow_user,
    check_follow_status,
    get_followers,
    get_following
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/follow",
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Follow a user",
    description="Follow another user."
)
async def follow_another_user(
    follow_req: FollowRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Follow another user.
    
    This endpoint allows a user to follow another user.
    """
    follower_id = current_user.id
    following_id = follow_req.user_id
    
    # Check if user IDs are valid
    if not ObjectId.is_valid(following_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if user is trying to follow themselves
    if follower_id == following_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    # Check if target user exists
    following_user = await get_user_by_id(following_id)
    if not following_user or not following_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to follow not found"
        )
    
    # Check if already following
    is_following = await check_follow_status(follower_id, following_id)
    if is_following:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already following this user"
        )
    
    # Follow user
    follow_result = await follow_user(follower_id, following_id)
    if not follow_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to follow user"
        )
    
    # Return follow response
    return {
        "follower_id": follower_id,
        "following_id": following_id,
        "created_at": follow_result["created_at"]
    }


@router.delete(
    "/unfollow/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unfollow a user",
    description="Unfollow a previously followed user."
)
async def unfollow_another_user(
    user_id: str = Path(..., description="ID of the user to unfollow"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Unfollow a previously followed user.
    
    This endpoint allows a user to unfollow another user.
    """
    follower_id = current_user.id
    following_id = user_id
    
    # Check if user IDs are valid
    if not ObjectId.is_valid(following_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if target user exists
    following_user = await get_user_by_id(following_id)
    if not following_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to unfollow not found"
        )
    
    # Check if actually following
    is_following = await check_follow_status(follower_id, following_id)
    if not is_following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not following this user"
        )
    
    # Unfollow user
    success = await unfollow_user(follower_id, following_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unfollow user"
        )
    
    # Return no content
    return None


@router.get(
    "/check/{user_id}",
    summary="Check follow status",
    description="Check if the current user follows a specific user."
)
async def check_follow(
    user_id: str = Path(..., description="ID of the user to check"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Check follow status.
    
    Check if the current user follows a specific user.
    """
    follower_id = current_user.id
    following_id = user_id
    
    # Check if user IDs are valid
    if not ObjectId.is_valid(following_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check follow status
    is_following = await check_follow_status(follower_id, following_id)
    
    # Return status
    return {"is_following": is_following}


@router.get(
    "/{user_id}/followers",
    response_model=PaginatedResponse,
    summary="Get user followers",
    description="Get the followers of a specific user."
)
async def get_user_followers(
    user_id: str = Path(..., description="ID of the user"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Get user followers.
    
    Get a paginated list of users who follow a specific user.
    """
    # Check if user ID is valid
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate skip based on page and limit
    skip = (page - 1) * limit
    
    # Get followers with pagination
    result = await get_followers(user_id, skip, limit)
    
    # Process followers to add is_following field
    for follower in result["data"]:
        if "follower" in follower:
            follower_id = str(follower["follower"]["_id"])
            is_following = await check_follow_status(current_user.id, follower_id)
            follower["follower"]["is_following"] = is_following
    
    return result


@router.get(
    "/{user_id}/following",
    response_model=PaginatedResponse,
    summary="Get users followed by user",
    description="Get the users that a specific user follows."
)
async def get_user_following(
    user_id: str = Path(..., description="ID of the user"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserData = Depends(get_current_user)
):
    """
    Get users followed by user.
    
    Get a paginated list of users that a specific user follows.
    """
    # Check if user ID is valid
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate skip based on page and limit
    skip = (page - 1) * limit
    
    # Get following with pagination
    result = await get_following(user_id, skip, limit)
    
    # Process following to add is_following field
    for following in result["data"]:
        if "following" in following:
            following_id = str(following["following"]["_id"])
            is_following = await check_follow_status(current_user.id, following_id)
            following["following"]["is_following"] = is_following
    
    return result