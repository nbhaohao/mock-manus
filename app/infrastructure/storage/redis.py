from functools import lru_cache

from core.config import Settings, get_settings
import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisClient:

    def __init__(self):
        self._client: Redis | None = None
        self._settings: Settings = get_settings()

    async def init(self) -> None:
        if self._client:
            logger.warning("Redis client already initialized")
            return
        try:
            self._client = Redis(
                host=self._settings.redis_host,
                port=self._settings.redis_port,
                db=self._settings.redis_db,
                password=self._settings.redis_password,
                decode_responses=True
            )
            await self._client.ping()
            logger.info("Redis client initialized")

        except Exception as e:
            logger.error(f"Redis client initialization failed: {str(e)}")
            raise e

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("Redis client closed")

        get_redis.cache_clear()

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client not initialized")
        return self._client


@lru_cache()
def get_redis() -> RedisClient:
    return RedisClient()
