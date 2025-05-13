from fastapi import APIRouter, Depends
from ..auth import get_current_user

router = APIRouter()

@router.get("/api/auth/validate")
async def validate_token(user: dict = Depends(get_current_user)):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "email": user["email"],
        "role": user.get("role", "user")
    }