from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, conlist, constr

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    comment_id: str
    author_id: str
    author_name: str
    created_at: datetime

class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    media_urls: conlist(str, max_items=5)
    tags: Optional[List[str]] = Field(None, max_length=10)

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    media_urls: List[constr(max_length=200)]
    tags: Optional[List[str]] = Field(None, max_length=10)

class Post(PostBase):
    id: str
    author_id: str
    author_name: str
    created_at: datetime
    updated_at: datetime
    likes: int = 0
    liked_by: List[str] = []
    comments: List[Comment] = []

    class Config:
        orm_mode = True

class TimelineParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

class UserPostsParams(BaseModel):
    user_id: str
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

class SearchPostsParams(BaseModel):
    query: str = Field(..., min_length=1)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

class LikePostResponse(BaseModel):
    post_id: str
    liked: bool
    likes_count: int

class ErrorResponse(BaseModel):
    detail: str