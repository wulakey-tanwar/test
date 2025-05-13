from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from ..database import (
    create_comment, get_comment_by_id, update_comment,
    delete_comment, get_comments, count_comments,
    like_comment, unlike_comment, delete_comments_by_post,
    get_comments_with_replies
)
from ..auth import get_current_user, get_optional_user, verify_post_exists
from ..models import (
    CommentCreate, CommentResponse, CommentInDB,
    CommentUpdate, PaginatedCommentsResponse, CommentWithReplies
)

logger = logging.getLogger("comment-service.routers.comments")

router = APIRouter(tags=["comments"])


def _comment_to_response(comment: Dict[str, Any], current_user_id: Optional[str] = None) -> CommentResponse:
    """Convert a comment document to a CommentResponse model"""
    user_has_liked = False
    if current_user_id:
        user_id = ObjectId(current_user_id)
        user_has_liked = user_id in comment.get("likes", [])
    
    return CommentResponse(
        id=str(comment["_id"]),
        post_id=str(comment["post_id"]),
        user_id=str(comment["user_id"]),
        username=comment["username"],
        content=comment["content"],
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        is_edited=comment["is_edited"],
        parent_id=str(comment["parent_id"]) if comment.get("parent_id") else None,
        likes_count=len(comment.get("likes", [])),
        user_has_liked=user_has_liked
    )


async def _verify_post(post_id: str) -> None:
    """Verify post exists and raise appropriate exception if not"""
    if not await verify_post_exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )


async def _get_and_verify_comment(comment_id: str) -> Dict[str, Any]:
    """Get comment by ID and verify it exists"""
    comment = await get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


async def _verify_comment_ownership(comment: Dict[str, Any], current_user: Dict[str, Any], 
                                    allow_admin: bool = False) -> None:
    """Verify current user owns the comment or is admin if allowed"""
    is_owner = str(comment["user_id"]) == current_user["user_id"]
    is_admin = allow_admin and current_user.get("is_admin", False)
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    comment: CommentCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new comment"""
    try:
        # Verify the post exists
        await _verify_post(str(comment.post_id))
        
        # Prepare comment data
        comment_data = CommentInDB(
            **comment.model_dump(),
            user_id=ObjectId(current_user["user_id"]),
            username=current_user.get("username", "User"),
        )
        
        # If this is a reply, verify the parent comment exists
        if comment.parent_id:
            parent_comment = await _get_and_verify_comment(str(comment.parent_id))
            
            # Ensure the parent comment belongs to the same post
            if str(parent_comment["post_id"]) != str(comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment does not belong to the specified post"
                )
        
        # Create the comment
        created_comment = await create_comment(comment_data.model_dump())
        if not created_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        
        return _comment_to_response(created_comment, current_user["user_id"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: str = Path(..., description="The ID of the comment to retrieve"),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """Get a comment by ID"""
    try:
        comment = await _get_and_verify_comment(comment_id)
        return _comment_to_response(
            comment, 
            current_user["user_id"] if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_existing_comment(
    comment_update: CommentUpdate,
    comment_id: str = Path(..., description="The ID of the comment to update"),
    current_user: Dict = Depends(get_current_user)
):
    """Update a comment"""
    try:
        # Get and verify comment exists
        comment = await _get_and_verify_comment(comment_id)
        
        # Verify ownership
        await _verify_comment_ownership(comment, current_user)
        
        # Prepare update data
        update_data = comment_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Add metadata for the update
        update_data["updated_at"] = datetime.utcnow()
        update_data["is_edited"] = True
        
        # Update the comment
        updated_comment = await update_comment(comment_id, update_data)
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
        
        return _comment_to_response(updated_comment, current_user["user_id"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_comment(
    comment_id: str = Path(..., description="The ID of the comment to delete"),
    current_user: Dict = Depends(get_current_user)
):
    """Delete a comment"""
    try:
        # Get and verify comment exists
        comment = await _get_and_verify_comment(comment_id)
        
        # Verify ownership (admins can also delete)
        await _verify_comment_ownership(comment, current_user, allow_admin=True)
        
        # Delete the comment
        if not await delete_comment(comment_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/posts/{post_id}/comments", response_model=PaginatedCommentsResponse)
async def list_comments_for_post(
    post_id: str = Path(..., description="The ID of the post"),
    parent_id: Optional[str] = Query(None, description="Filter by parent comment ID (for replies)"),
    limit: int = Query(20, ge=1, le=100, description="Number of comments to return"),
    skip: int = Query(0, ge=0, description="Number of comments to skip"),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """List comments for a post with optional pagination"""
    try:
        # Verify the post exists
        await _verify_post(post_id)
        
        # Set up filters
        filters = {
            "post_id": ObjectId(post_id),
            "parent_id": ObjectId(parent_id) if parent_id else None
        }
            
        # Get comments with pagination and count total
        comments_data = await get_comments(filters, [("created_at", -1)], limit, skip)
        total_comments = await count_comments(filters)
        
        # Transform MongoDB documents to response models
        comment_responses = [
            _comment_to_response(
                comment, 
                current_user["user_id"] if current_user else None
            ) for comment in comments_data
        ]
            
        # Create paginated response
        return PaginatedCommentsResponse(
            data=comment_responses,
            total=total_comments,
            page=(skip // limit) + 1,
            limit=limit,
            has_more=total_comments > (skip + limit)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/posts/{post_id}/comments/hierarchical", response_model=List[CommentWithReplies])
async def list_hierarchical_comments(
    post_id: str = Path(..., description="The ID of the post"),
    limit: int = Query(20, ge=1, le=50, description="Number of parent comments to return"),
    skip: int = Query(0, ge=0, description="Number of parent comments to skip"),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """List hierarchical comments (parent comments with their replies) for a post"""
    try:
        # Verify the post exists
        await _verify_post(post_id)
        
        # Get hierarchical comments
        result = await get_comments_with_replies(post_id, None, limit, skip)
        
        # Transform MongoDB documents to response models
        hierarchical_comments = []
        current_user_id = current_user["user_id"] if current_user else None
        
        for parent in result["data"]:
            # Convert parent comment
            parent_response = _comment_to_response(parent, current_user_id)
            
            # Create a CommentWithReplies instance with replies
            parent_with_replies = CommentWithReplies(**parent_response.model_dump())
            parent_with_replies.replies = [
                _comment_to_response(reply, current_user_id) 
                for reply in parent.get("replies", [])
            ]
            
            hierarchical_comments.append(parent_with_replies)
            
        return hierarchical_comments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing hierarchical comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/comments/{comment_id}/like", response_model=CommentResponse)
async def like_a_comment(
    comment_id: str = Path(..., description="The ID of the comment to like"),
    current_user: Dict = Depends(get_current_user)
):
    """Like a comment"""
    try:
        # Get and verify comment exists
        await _get_and_verify_comment(comment_id)
        
        # Add like
        await like_comment(comment_id, current_user["user_id"])
        
        # Get updated comment
        updated_comment = await get_comment_by_id(comment_id)
        
        return _comment_to_response(updated_comment, current_user["user_id"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/comments/{comment_id}/unlike", response_model=CommentResponse)
async def unlike_a_comment(
    comment_id: str = Path(..., description="The ID of the comment to unlike"),
    current_user: Dict = Depends(get_current_user)
):
    """Unlike a comment"""
    try:
        # Get and verify comment exists
        await _get_and_verify_comment(comment_id)
        
        # Remove like
        await unlike_comment(comment_id, current_user["user_id"])
        
        # Get updated comment
        updated_comment = await get_comment_by_id(comment_id)
        
        return _comment_to_response(updated_comment, current_user["user_id"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}/comments", response_model=PaginatedCommentsResponse)
async def list_comments_by_user(
    user_id: str = Path(..., description="The ID of the user"),
    limit: int = Query(20, ge=1, le=100, description="Number of comments to return"),
    skip: int = Query(0, ge=0, description="Number of comments to skip"),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """List comments by a specific user"""
    try:
        # Set up filters
        filters = {"user_id": ObjectId(user_id)}
        
        # Get comments with pagination and count total
        comments_data = await get_comments(filters, [("created_at", -1)], limit, skip)
        total_comments = await count_comments(filters)
        
        # Transform MongoDB documents to response models
        current_user_id = current_user["user_id"] if current_user else None
        comment_responses = [_comment_to_response(comment, current_user_id) for comment in comments_data]
            
        # Create paginated response
        return PaginatedCommentsResponse(
            data=comment_responses,
            total=total_comments,
            page=(skip // limit) + 1,
            limit=limit,
            has_more=total_comments > (skip + limit)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing user comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/posts/{post_id}/comments", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_comments_for_post(
    post_id: str = Path(..., description="The ID of the post"),
    current_user: Dict = Depends(get_current_user)
):
    """Delete all comments for a post (admin only)"""
    try:
        # Verify the post exists
        await _verify_post(post_id)
        
        # Check if the user is an admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action"
            )
        
        # Delete all comments for the post
        await delete_comments_by_post(post_id)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )