import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument, ASCENDING, DESCENDING, IndexModel
import os
from dotenv import load_dotenv
from bson.errors import InvalidId
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Collections
USERS_COLLECTION = "users"
FOLLOWERS_COLLECTION = "followers"

# Global database client
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def init_db():
    """Initialize database connection and create indexes."""
    global client, db
    
    try:
        # Create client with connection pooling
        client = AsyncIOMotorClient(
            MONGODB_URL, 
            maxPoolSize=10, 
            minPoolSize=5,
            serverSelectionTimeoutMS=5000
        )
        
        # Get database reference
        db = client[DATABASE_NAME]
        
        # Create indexes for better query performance
        await create_indexes()
        
        # Verify connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {MONGODB_URL}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """Close database connection."""
    if client:
        client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for optimized queries."""
    # Users collection indexes
    user_indexes = [
        IndexModel([("username", ASCENDING)], unique=True),
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
    ]
    
    # Followers collection indexes
    follower_indexes = [
        IndexModel([("follower_id", ASCENDING), ("following_id", ASCENDING)], unique=True),
        IndexModel([("follower_id", ASCENDING)]),
        IndexModel([("following_id", ASCENDING)]),
    ]
    
    # Create indexes
    await db[USERS_COLLECTION].create_indexes(user_indexes)
    await db[FOLLOWERS_COLLECTION].create_indexes(follower_indexes)
    
    logger.info("Database indexes created successfully")


# User operations
async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    try:
        # First try to find by _id
        try:
            user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
            if user:
                return user
        except InvalidId:
            # If ObjectId conversion fails, continue to next lookup
            pass
            
        # If not found by _id, try user_id field
        user = await db[USERS_COLLECTION].find_one({"user_id": user_id})
        return user
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}")
        return None


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    try:
        return await db[USERS_COLLECTION].find_one({"username": username.lower()})
    except Exception as e:
        logger.error(f"Error fetching user by username: {e}")
        return None


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email."""
    try:
        return await db[USERS_COLLECTION].find_one({"email": email.lower()})
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return None


async def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a new user."""
    try:
        result = await db[USERS_COLLECTION].insert_one(user_data)
        if result.inserted_id:
            return await get_user_by_id(str(result.inserted_id))
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


async def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update user profile."""
    try:
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update and return the updated document
        return await db[USERS_COLLECTION].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return None


async def delete_user(user_id: str) -> bool:
    """Soft delete a user by setting is_active to False."""
    try:
        result = await db[USERS_COLLECTION].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False


async def get_users(skip: int = 0, limit: int = 20) -> Dict[str, Any]:
    try:
        # Convert MongoDB cursor to list first
        cursor = db[USERS_COLLECTION].find(
            {"is_active": True},
            projection={
                "_id": 1,
                "username": 1,
                "full_name": 1,
                # Include other needed fields
            }
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        users = await cursor.to_list(length=limit)
        
        # Convert ObjectId and datetime fields
        for user in users:
            user["_id"] = str(user["_id"])
            if isinstance(user.get("created_at"), datetime):
                user["created_at"] = user["created_at"].isoformat()
                
        total = await db[USERS_COLLECTION].count_documents({"is_active": True})
        
        return {
            "data": users,
            "page": skip // limit + 1,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return {"data": [], "total": 0, "page": 1, "limit": limit}


# Follower operations
async def follow_user(follower_id: str, following_id: str) -> Optional[Dict[str, Any]]:
    """Create a follow relationship between users."""
    try:
        try:
            follower_obj_id = ObjectId(follower_id)
            following_obj_id = ObjectId(following_id)
        except InvalidId:
            logger.error("Invalid ObjectId format for follower or following ID")
            return None

        # Check if users exist
        follower = await get_user_by_id(follower_id)
        following = await get_user_by_id(following_id)

        if not follower or not following:
            logger.warning(f"Either follower or following user not found: {follower_id}, {following_id}")
            return None

        # Check if already following
        already_following = await db[FOLLOWERS_COLLECTION].find_one({
            "follower_id": follower_obj_id,
            "following_id": following_obj_id
        })
        if already_following:
            logger.info(f"User {follower_id} already follows {following_id}")
            return None

        # Create follower relationship
        follow_data = {
            "follower_id": follower_obj_id,
            "following_id": following_obj_id,
            "created_at": datetime.utcnow()
        }

        result = await db[FOLLOWERS_COLLECTION].insert_one(follow_data)

        if result.inserted_id:
            # Update following_count of the follower
            follower_update = await db[USERS_COLLECTION].update_one(
                {"_id": follower_obj_id},
                {"$inc": {"following_count": 1}}
            )
            logger.info(f"Following count updated for follower {follower_id}: matched={follower_update.matched_count}")

            # Update follower_count of the followed user
            following_update = await db[USERS_COLLECTION].update_one(
                {"_id": following_obj_id},
                {"$inc": {"follower_count": 1}}
            )
            logger.info(f"Follower count updated for following {following_id}: matched={following_update.matched_count}")

            follow_data["_id"] = str(result.inserted_id)
            return follow_data

        return None

    except Exception as e:
        logger.error(f"Error following user: {e}")
        return None

async def unfollow_user(follower_id: str, following_id: str) -> bool:
    """Remove a follow relationship between users."""
    try:
        try:
            follower_obj_id = ObjectId(follower_id)
            following_obj_id = ObjectId(following_id)
        except InvalidId:
            logger.error("Invalid ObjectId format for follower or following ID")
            return False

        # Check if follow relationship exists
        existing_follow = await db[FOLLOWERS_COLLECTION].find_one({
            "follower_id": follower_obj_id,
            "following_id": following_obj_id
        })

        if not existing_follow:
            logger.info(f"No follow relationship found between {follower_id} and {following_id}")
            return False

        # Remove follow relationship
        result = await db[FOLLOWERS_COLLECTION].delete_one({
            "follower_id": follower_obj_id,
            "following_id": following_obj_id
        })

        if result.deleted_count > 0:
            # Decrement following_count for the follower
            follower_update = await db[USERS_COLLECTION].update_one(
                {"_id": follower_obj_id},
                {"$inc": {"following_count": -1}}
            )
            logger.info(f"Decremented following_count for user {follower_id}: matched={follower_update.matched_count}")

            # Decrement follower_count for the followed user
            following_update = await db[USERS_COLLECTION].update_one(
                {"_id": following_obj_id},
                {"$inc": {"follower_count": -1}}
            )
            logger.info(f"Decremented follower_count for user {following_id}: matched={following_update.matched_count}")

            return True

        return False
    except Exception as e:
        logger.error(f"Error unfollowing user: {e}")
        return False

async def check_follow_status(follower_id: str, following_id: str) -> bool:
    """Check if one user follows another."""
    try:
        try:
            follower_obj_id = ObjectId(follower_id)
            following_obj_id = ObjectId(following_id)
        except InvalidId:
            logger.warning("Invalid ObjectId format for follower_id or following_id")
            return False

        result = await db[FOLLOWERS_COLLECTION].find_one({
            "follower_id": follower_obj_id,
            "following_id": following_obj_id
        })
        return result is not None

    except Exception as e:
        logger.error(f"Error checking follow status: {e}")
        return False


async def get_followers(user_id: str, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
    """Get users who follow a specified user."""
    try:
        try:
            user_obj_id = ObjectId(user_id)
        except InvalidId:
            logger.warning("Invalid ObjectId format for user_id in get_followers")
            return {"data": [], "page": 1, "limit": limit, "total": 0, "total_pages": 0}

        # Get total count for pagination
        total = await db[FOLLOWERS_COLLECTION].count_documents({"following_id": user_obj_id})

        # Aggregation pipeline
        pipeline = [
            {"$match": {"following_id": user_obj_id}},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$lookup": {
                "from": USERS_COLLECTION,
                "localField": "follower_id",
                "foreignField": "_id",
                "as": "follower_info"
            }},
            {"$unwind": "$follower_info"},
            {"$project": {
                "_id": 1,
                "created_at": 1,
                "follower": "$follower_info"
            }}
        ]

        cursor = db[FOLLOWERS_COLLECTION].aggregate(pipeline)
        followers = await cursor.to_list(length=limit)

        return {
            "data": followers,
            "page": skip // limit + 1,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        logger.error(f"Error fetching followers: {e}")
        return {"data": [], "page": 1, "limit": limit, "total": 0, "total_pages": 0}


async def get_following(user_id: str, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
    """Get users that a specified user follows."""
    try:
        try:
            user_obj_id = ObjectId(user_id)
        except InvalidId:
            logger.warning("Invalid ObjectId format for user_id in get_following")
            return {"data": [], "page": 1, "limit": limit, "total": 0, "total_pages": 0}

        # Get total count for pagination
        total = await db[FOLLOWERS_COLLECTION].count_documents({"follower_id": user_obj_id})

        # Get following IDs with pagination
        pipeline = [
            {"$match": {"follower_id": user_obj_id}},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$lookup": {
                "from": USERS_COLLECTION,
                "localField": "following_id",
                "foreignField": "_id",
                "as": "following_info"
            }},
            {"$unwind": "$following_info"},
            {"$project": {
                "_id": 1,
                "created_at": 1,
                "following": "$following_info"
            }}
        ]

        cursor = db[FOLLOWERS_COLLECTION].aggregate(pipeline)
        following = await cursor.to_list(length=limit)

        return {
            "data": following,
            "page": skip // limit + 1,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        logger.error(f"Error fetching following users: {e}")
        return {"data": [], "page": 1, "limit": limit, "total": 0, "total_pages": 0}