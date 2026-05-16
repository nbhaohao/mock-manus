import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus
from app.infrastructure.storage.redis import RedisClient

logger = logging.getLogger(__name__)


class RedisHealthChecker(HealthChecker):

    def __init__(self, redis_client: AsyncSession) -> None:
        self._redis_client = redis_client

    async def check(self) -> HealthStatus:
        try:
            if await self._redis_client.client.ping():
                return HealthStatus(service="redis", status="ok")
            else:
                return HealthStatus(service="redis", status="error", details="Redis service ping failed")
        except Exception as e:
            logger.error(f"Redis HealthChecker failed with exception: {str(e)}")
            return HealthStatus(
                service="redis",
                status="error",
                details=str(e)
            )
