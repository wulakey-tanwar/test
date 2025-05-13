from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
import re

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v.lower()

    @validator('website')
    def website_valid(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    
    @validator('website')
    def website_valid(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v


class UserProfileInDB(UserProfileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    follower_count: int = 0
    following_count: int = 0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
        schema_extra = {
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "bio": "Software engineer and hobby photographer",
                "avatar_url": "https://example.com/avatars/johndoe.jpg",
                "location": "San Francisco, CA",
                "website": "https://johndoe.com",
                "created_at": "2023-01-15T08:00:00",
                "updated_at": "2023-01-15T08:00:00",
                "is_active": True,
                "follower_count": 42,
                "following_count": 37
            }
        }


# Update UserProfileResponse model
class UserProfileResponse(BaseModel):
    id: str = Field(..., alias="_id")
    username: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: str  # Changed from datetime to string
    follower_count: int
    following_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True


class FollowRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user to follow/unfollow")


class FollowResponse(BaseModel):
    follower_id: str
    following_id: str
    created_at: datetime
    
    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class FollowRelationship(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    follower_id: str
    following_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}


class PaginatedResponse(BaseModel):
    data: List[Any]
    page: int
    limit: int
    total: int
    total_pages: int
    
    class Config:
        arbitrary_types_allowed = True