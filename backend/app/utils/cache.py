import json
import logging
from typing import Any, Optional, List
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """
    High-performance Redis-based caching engine with tag-based invalidation.
    Designed for fast read caching and distributed invalidation on mutations.
    """
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URI, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        try:
            val = await self.redis.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 60, tags: Optional[List[str]] = None):
        try:
            pipeline = self.redis.pipeline()
            pipeline.setex(key, ttl_seconds, json.dumps(value))
            if tags:
                for tag in tags:
                    pipeline.sadd(f"tag:{tag}", key)
                    pipeline.expire(f"tag:{tag}", ttl_seconds * 2) # keep tag mapping slightly longer
            await pipeline.execute()
        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")

    async def invalidate_key(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis invalidate_key error for {key}: {e}")

    async def invalidate_tags(self, tags: List[str] | str):
        if isinstance(tags, str):
            tags = [tags]
        try:
            pipeline = self.redis.pipeline()
            for tag in tags:
                keys = await self.redis.smembers(f"tag:{tag}")
                if keys:
                    pipeline.delete(*keys)
                pipeline.delete(f"tag:{tag}")
            await pipeline.execute()
        except Exception as e:
            logger.error(f"Redis invalidate_tags error: {e}")

    async def clear(self):
        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

# Singleton cache instance
cache = CacheManager()
