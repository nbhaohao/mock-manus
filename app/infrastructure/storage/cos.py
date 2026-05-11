import logging
from functools import lru_cache
from typing import Optional

from qcloud_cos import CosS3Client, CosConfig

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Cos:

    def __init__(self):
        self._settings: Settings = get_settings()
        self._client: Optional[CosS3Client] = None

    async def init(self) -> None:
        if self._client is not None:
            logger.warning("Cos Storage already initialized")
            return
        try:
            config = CosConfig(
                Region=self._settings.cos_region,
                SecretId=self._settings.cos_secret_id,
                SecretKey=self._settings.cos_secret_key,
                Token=None,
                Scheme=self._settings.cos_scheme
            )
            self._client = CosS3Client(config)
            logger.info("Cos Storage initialized")
        except Exception as e:
            logger.error(f"Cos Storage initialization failed: {str(e)}")
            raise e

    async def shutdown(self) -> None:
        if self._client is not None:
            self._client = None
            logger.info("Cos Storage shutdown successful")
        get_cos.cache_clear()

    @property
    def client(self) -> CosS3Client:
        if self._client is None:
            raise RuntimeError("Cos Storage not initialized")
        return self._client


@lru_cache()
def get_cos() -> Cos:
    return Cos()
