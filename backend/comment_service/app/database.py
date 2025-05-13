import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING, IndexModel
from bson import ObjectId
from typing import Dict, List, Optional, Any
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("comment-service.database")

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COMMENT_COLLECTION = "comments"

# MongoDB client instance and database
client = None
db = None


async def init_db():
    """Initialize the database connection and set up indexes"""
    global client, db
    
    try:
        # Create MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI, maxPoolSize=10)
        db = client[DB_NAME]
        
        # Create indexes for better query performance
        comment_indexes = [
            IndexModel([("post_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("parent_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            # Compound index for hierarchical comments
            IndexModel([("post_id", ASCENDING), ("parent_id", ASCENDING), ("created_at", DESCENDING)])
        ]
        
        await db[COMMENT_COLLECTION].create_indexes(comment_indexes)
        logger.info(f"Connected to MongoDB at {MONGO_URI} and created indexes")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_db():
    """Close the database connection"""
    if client:
        client.close()
        logger.info("MongoDB connection closed")


async def get_comments_collection():
    """Get the comments collection"""
    return db[COMMENT_COLLECTION]


async def create_comment(comment_data: Dict) -> Dict:
    """Create a new comment"""
    collection = await get_comments_collection()
    result = await collection.insert_one(comment_data)
    if result.inserted_id:
        return await get_comment_by_id(result.inserted_id)
    return None


async def get_comment_by_id(comment_id: str) -> Optional[Dict]:
    """Get a comment by its ID"""
    try:
        collection = await get_comments_collection()
        comment = await collection.find_one({"_id": ObjectId(comment_id)})
        return comment
    except Exception as e:
        logger.error(f"Error retrieving comment {comment_id}: {str(e)}")
        return None


async def update_comment(comment_id: str, update_data: Dict) -> Optional[Dict]:
    """Update a comment"""
    try:
        collection = await get_comments_collection()
        result = await collection.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            return await get_comment_by_id(comment_id)
        return None
    except Exception as e:
        logger.error(f"Error updating comment {comment_id}: {str(e)}")
        return None


async def delete_comment(comment_id: str) -> bool:
    """Delete a comment"""
    try:
        collection = await get_comments_collection()
        result = await collection.delete_one({"_id": ObjectId(comment_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        return False


async def get_comments(
    filters: Dict = None,
    sort_by: List = None,
    limit: int = 50,
    skip: int = 0
) -> List[Dict]:
    """Get comments with filters and pagination"""
    try:
        collection = await get_comments_collection()
        query = filters or {}
        cursor = collection.find(query)
        
        # Apply sorting
        if sort_by:
            cursor = cursor.sort(sort_by)
        else:
            cursor = cursor.sort("created_at", DESCENDING)
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        # Execute query and return results as list
        return await cursor.to_list(length=limit)
    except Exception as e:
        logger.error(f"Error fetching comments: {str(e)}")
        return []


async def count_comments(filters: Dict = None) -> int:
    """Count comments matching the given filters"""
    try:
        collection = await get_comments_collection()
        query = filters or {}
        return await collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error counting comments: {str(e)}")
        return 0


async def like_comment(comment_id: str, user_id: str) -> bool:
    """Add a user like to a comment"""
    try:
        collection = await get_comments_collection()
        result = await collection.update_one(
            {"_id": ObjectId(comment_id), "likes": {"$ne": ObjectId(user_id)}},
            {"$addToSet": {"likes": ObjectId(user_id)}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {str(e)}")
        return False


async def unlike_comment(comment_id: str, user_id: str) -> bool:
    """Remove a user like from a comment"""
    try:
        collection = await get_comments_collection()
        result = await collection.update_one(
            {"_id": ObjectId(comment_id)},
            {"$pull": {"likes": ObjectId(user_id)}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error unliking comment {comment_id}: {str(e)}")
        return False


async def delete_comments_by_post(post_id: str) -> int:
    """Delete all comments for a specific post"""
    try:
        collection = await get_comments_collection()
        result = await collection.delete_many({"post_id": ObjectId(post_id)})
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting comments for post {post_id}: {str(e)}")
        return 0


async def get_comments_with_replies(post_id: str, parent_id: Optional[str] = None, limit: int = 10, skip: int = 0) -> Dict[str, Any]:
    """Get hierarchical comments with replies"""
    try:
        collection = await get_comments_collection()
        
        # Query for parent comments
        parent_filter = {
            "post_id": ObjectId(post_id),
            "parent_id": None if parent_id is None else ObjectId(parent_id)
        }
        
        # Get total count of parent comments
        total = await collection.count_documents(parent_filter)
        
        # Get parent comments with pagination
        parents = await collection.find(parent_filter) \
            .sort("created_at", DESCENDING) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        # For each parent, get its replies
        for parent in parents:
            replies = await collection.find({"parent_id": parent["_id"]}) \
                .sort("created_at", ASCENDING) \
                .to_list(length=None)
            parent["replies"] = replies
        
        return {
            "data": parents,
            "total": total,
            "page": skip // limit + 1,
            "limit": limit,
            "has_more": total > (skip + limit)
        }
    except Exception as e:
        logger.error(f"Error fetching comments with replies: {str(e)}")
        return {"data": [], "total": 0, "page": 1, "limit": limit, "has_more": False}