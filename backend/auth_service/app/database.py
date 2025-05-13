from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from bson import ObjectId
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from pymongo import IndexModel, ASCENDING
from pymongo.collection import Collection  # Only used for typing in some cases

# Load environment variables
load_dotenv()

logger = logging.getLogger("auth-service.database")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Global client & db initialized during app startup
client: AsyncIOMotorClient = None
db = None


async def init_db():
    global client, db
    logger.info("Connecting to MongoDB")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db["users"]

    # Create indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("username", unique=True)

    logger.info("Database initialized")


# For dependency injection
def get_users_collection() -> AsyncIOMotorCollection:
    return db["users"]


class PyObjectId(ObjectId):
    @classmethod
    def _get_validators_(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def _modify_schema_(cls, field_schema):
        field_schema.update(type="string")


# ✅ Create user with injected collection
async def create_user(user_data: dict, users_collection: AsyncIOMotorCollection):
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await users_collection.insert_one(user_data)
        user = await users_collection.find_one({"_id": result.inserted_id})
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


# ✅ Get user by email with injected collection
async def get_user_by_email(email: str, users_collection: AsyncIOMotorCollection):
    return await users_collection.find_one({"email": email})


# ✅ Still uses global collection — can be refactored later
async def get_user_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    return await db["users"].find_one({"_id": ObjectId(user_id)})