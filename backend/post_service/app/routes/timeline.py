from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any

from ..models import Post, TimelineParams
from ..database import Database
from ..auth import Auth

router = APIRouter(prefix="/timeline", tags=["timeline"])

@router.get("/", response_model=List[Post])
async def get_timeline(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """
    Get timeline posts (posts from followed users)
    """
    user_id = current_user["id"]
    token = current_user.get("token", "")
    
    # Get the IDs of users that the current user follows
    following_ids = await Auth.get_following_ids(user_id, token)
    
    # Include the user's own posts in the timeline
    user_ids = [user_id] + following_ids
    
    # Get posts for the timeline
    posts = await Database.get_timeline(user_ids, skip, limit)
    return posts

@router.get("/discover", response_model=List[Post])
async def discover_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """
    Discover new posts (a simple discovery algorithm that returns recent posts)
    In a real application, this could be more sophisticated with personalization
    """
    # This is a simplified version - in production you might want to:
    # 1. Exclude posts from users the current user already follows
    # 2. Prioritize posts with more engagement 
    # 3. Consider user interests and post content for better recommendations
    # 4. Consider location or other factors
    
    # For now, we'll just get recent posts with higher like counts
    # This would need a more complex query in a real application
    async with Database.client.start_session() as session:
        pipeline = [
            {"$sort": {"likes": -1, "created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        cursor = Database.post_collection.aggregate(pipeline)
        posts = []
        async for post in cursor:
            posts.append(Database._format_post(post))
        
        return posts

@router.get("/trending", response_model=List[Post])
async def trending_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    time_window: str = Query("day", enum=["hour", "day", "week"]),
    current_user: Dict = Depends(Auth.get_current_user)
):
    """
    Get trending posts based on recent engagement
    """
    import datetime
    
    # Calculate the time window
    now = datetime.datetime.utcnow()
    if time_window == "hour":
        start_time = now - datetime.timedelta(hours=1)
    elif time_window == "day":
        start_time = now - datetime.timedelta(days=1)
    else:  # week
        start_time = now - datetime.timedelta(weeks=1)
    
    # Aggregate pipeline to find trending posts
    # This is a simplified version - in production, you might want a more sophisticated algorithm
    async with Database.client.start_session() as session:
        pipeline = [
            {"$match": {"created_at": {"$gte": start_time}}},
            # Calculate a trending score (simplified)
            # In a real app, you might use more factors like comment velocity, user reach, etc.
            {"$addFields": {
                "trending_score": {
                    "$add": [
                        "$likes",
                        {"$multiply": [{"$size": {"$ifNull": ["$comments", []]}}, 3]}
                    ]
                }
            }},
            {"$sort": {"trending_score": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        cursor = Database.post_collection.aggregate(pipeline)
        posts = []
        async for post in cursor:
            posts.append(Database._format_post(post))
        
        return posts