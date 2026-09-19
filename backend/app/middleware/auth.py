from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from bson import ObjectId
from app.database import get_db
from app.utils.security import verify_token
from app.models.mongo_utils import serialize_doc
from app.utils.cache import cache

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(security)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")

    token = credentials.credentials
    try:
        payload = verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    user_id = payload.get("id")
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    # Check fast in-memory user cache first
    cache_key = f"auth_user:{user_id}"
    cached_user = await cache.get(cache_key)
    if cached_user is not None:
        return dict(cached_user)

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists.")

    user.pop("passwordHash", None)
    serialized = serialize_doc(user)
    await cache.set(cache_key, serialized, ttl_seconds=30, tags=[f"user:{user_id}", "users"])
    return dict(serialized)

def require_role(*roles: str):
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not current_user or current_user.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action."
            )
        return current_user
    return role_checker
