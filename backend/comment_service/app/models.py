from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    
    class Config:
        populate_by_name = True


class CommentCreate(CommentBase):
    post_id: PyObjectId


class CommentInDB(CommentBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    post_id: PyObjectId
    user_id: PyObjectId
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_edited: bool = False
    parent_id: Optional[PyObjectId] = None
    likes: List[PyObjectId] = []
    
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class CommentResponse(CommentBase):
    id: str
    post_id: str
    user_id: str
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_edited: bool
    parent_id: Optional[str] = None
    likes_count: int
    user_has_liked: bool = False
    
    class Config:
        populate_by_name = True


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    
    class Config:
        populate_by_name = True


class CommentWithReplies(CommentResponse):
    replies: List["CommentResponse"] = []


class CommentFilters(BaseModel):
    post_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_id: Optional[str] = None
    limit: int = 50
    skip: int = 0


class LikeComment(BaseModel):
    comment_id: PyObjectId


class PaginatedCommentsResponse(BaseModel):
    data: List[CommentResponse]
    total: int
    page: int
    limit: int
    has_more: bool