from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    client: AsyncIOMotorClient = None
    post_collection = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        
        cls.client = AsyncIOMotorClient(mongo_url)
        db = cls.client[db_name]
        cls.post_collection = db.posts
        
        # Create indexes
        await cls.post_collection.create_index([("author_id", ASCENDING)])
        await cls.post_collection.create_index([("created_at", DESCENDING)])
        await cls.post_collection.create_index([("tags", ASCENDING)])
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
    
    @classmethod
    async def create_post(cls, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new post"""
        post_data["created_at"] = datetime.utcnow()
        post_data["updated_at"] = post_data["created_at"]
        post_data["likes"] = 0
        post_data["liked_by"] = []
        post_data["comments"] = []
        
        result = await cls.post_collection.insert_one(post_data)
        post = await cls.post_collection.find_one({"_id": result.inserted_id})
        return cls._format_post(post)
    
    @classmethod
    async def get_post(cls, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a post by ID"""
        try:
            post = await cls.post_collection.find_one({"_id": ObjectId(post_id)})
            return cls._format_post(post) if post else None
        except Exception:
            return None
    
    @classmethod
    async def update_post(cls, post_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a post"""
        update_data["updated_at"] = datetime.utcnow()
        try:
            result = await cls.post_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": update_data}
            )
            if result.modified_count:
                return await cls.get_post(post_id)
            return None
        except Exception:
            return None
    
    @classmethod
    async def delete_post(cls, post_id: str) -> bool:
        """Delete a post"""
        try:
            result = await cls.post_collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    @classmethod
    async def like_post(cls, post_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Like a post"""
        try:
            # Check if user already liked the post
            post = await cls.post_collection.find_one({
                "_id": ObjectId(post_id),
                "liked_by": user_id
            })
            
            if post:
                # User already liked the post, unlike it
                result = await cls.post_collection.update_one(
                    {"_id": ObjectId(post_id)},
                    {
                        "$pull": {"liked_by": user_id},
                        "$inc": {"likes": -1},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            else:
                # User hasn't liked the post, like it
                result = await cls.post_collection.update_one(
                    {"_id": ObjectId(post_id)},
                    {
                        "$addToSet": {"liked_by": user_id},
                        "$inc": {"likes": 1},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            
            if result.modified_count:
                return await cls.get_post(post_id)
            return None
        except Exception:
            return None
    
    @classmethod
    async def add_comment(cls, post_id: str, comment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add a comment to a post"""
        try:
            comment_data["created_at"] = datetime.utcnow()
            comment_data["comment_id"] = str(ObjectId())
            
            result = await cls.post_collection.update_one(
                {"_id": ObjectId(post_id)},
                {
                    "$push": {"comments": comment_data},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count:
                return await cls.get_post(post_id)
            return None
        except Exception:
            return None
    
    @classmethod
    async def delete_comment(cls, post_id: str, comment_id: str) -> Optional[Dict[str, Any]]:
        """Delete a comment from a post"""
        try:
            result = await cls.post_collection.update_one(
                {"_id": ObjectId(post_id)},
                {
                    "$pull": {"comments": {"comment_id": comment_id}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count:
                return await cls.get_post(post_id)
            return None
        except Exception:
            return None
    
    @classmethod
    async def get_user_posts(cls, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all posts by a specific user"""
        cursor = cls.post_collection.find({"author_id": user_id}).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        posts = []
        async for post in cursor:
            posts.append(cls._format_post(post))
        return posts
    
    @classmethod
    async def get_timeline(cls, user_ids: List[str], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get posts for timeline (posts from users that the current user follows)"""
        cursor = cls.post_collection.find({"author_id": {"$in": user_ids}}).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        posts = []
        async for post in cursor:
            posts.append(cls._format_post(post))
        return posts
    
    @classmethod
    async def search_posts(cls, query: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts by content or tags"""
        cursor = cls.post_collection.find({
            "$or": [
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        }).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        posts = []
        async for post in cursor:
            posts.append(cls._format_post(post))
        return posts
    
    @staticmethod
    def _format_post(post: Dict[str, Any]) -> Dict[str, Any]:
        """Format post for API response"""
        if post:
            post["id"] = str(post["_id"])
            del post["_id"]
        return post