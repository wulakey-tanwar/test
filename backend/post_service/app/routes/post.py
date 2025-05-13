from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Dict, Any, Optional

from ..models import (
    Post, PostCreate, PostUpdate, CommentCreate, 
    LikePostResponse, UserPostsParams, SearchPostsParams
)
from ..database import Database
from ..auth import Auth

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Create a new post"""
    user_id = current_user["id"]
    user_name = current_user.get("name", "User")
    
    post_dict = post_data.dict()
    post_dict["author_id"] = user_id
    post_dict["author_name"] = user_name
    
    post = await Database.create_post(post_dict)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )
    
    return post

@router.get("/{post_id}", response_model=Post)
async def get_post(
    post_id: str = Path(..., title="The ID of the post to get"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Get a post by ID"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post

@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_data: PostUpdate,
    post_id: str = Path(..., title="The ID of the post to update"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Update a post"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    user_id = current_user["id"]
    if not await Auth.verify_post_ownership(user_id, post["author_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    update_dict = {k: v for k, v in post_data.dict().items() if v is not None}
    updated_post = await Database.update_post(post_id, update_dict)
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post"
        )
    
    return updated_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str = Path(..., title="The ID of the post to delete"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Delete a post"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    user_id = current_user["id"]
    if not await Auth.verify_post_ownership(user_id, post["author_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    deleted = await Database.delete_post(post_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post"
        )

@router.post("/{post_id}/like", response_model=Post)
async def like_post(
    post_id: str = Path(..., title="The ID of the post to like"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Like or unlike a post"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    user_id = current_user["id"]
    updated_post = await Database.like_post(post_id, user_id)
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like/unlike post"
        )
    
    return updated_post

@router.post("/{post_id}/comments", response_model=Post)
async def add_comment(
    comment_data: CommentCreate,
    post_id: str = Path(..., title="The ID of the post to comment on"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Add a comment to a post"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    user_id = current_user["id"]
    user_name = current_user.get("name", "User")
    
    comment_dict = comment_data.dict()
    comment_dict["author_id"] = user_id
    comment_dict["author_name"] = user_name
    
    updated_post = await Database.add_comment(post_id, comment_dict)
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )
    
    return updated_post

@router.delete("/{post_id}/comments/{comment_id}", response_model=Post)
async def delete_comment(
    post_id: str = Path(..., title="The ID of the post"),
    comment_id: str = Path(..., title="The ID of the comment to delete"),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Delete a comment from a post"""
    post = await Database.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Find the comment
    comment = None
    for c in post.get("comments", []):
        if c.get("comment_id") == comment_id:
            comment = c
            break
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author of the comment or the post
    user_id = current_user["id"]
    if not (user_id == comment.get("author_id") or user_id == post["author_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    updated_post = await Database.delete_comment(post_id, comment_id)
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )
    
    return updated_post

@router.get("/user/{user_id}", response_model=List[Post])
async def get_user_posts(
    user_id: str = Path(..., title="User ID to get posts for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Get all posts from a specific user"""
    posts = await Database.get_user_posts(user_id, skip, limit)
    return posts

@router.get("/search", response_model=List[Post])
async def search_posts(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """Search posts by content or tags"""
    posts = await Database.search_posts(query, skip, limit)
    return posts