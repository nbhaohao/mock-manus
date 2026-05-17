import asyncio
import logging
import uuid
from typing import Any, Tuple, Optional

from app.domain.external.message_queue import MessageQueue
from app.infrastructure.storage.redis import get_redis

logger = logging.getLogger(__name__)


class RedisStreamMessageQueue(MessageQueue):
    def __init__(self, stream_name: str) -> None:
        self._stream_name = stream_name
        self._redis = get_redis()
        self._lock_expire_seconds = 10

    async def _acquire_lock(self, lock_key: str, timeout_seconds: int = 5) -> Optional[str]:
        lock_value = uuid.uuid4()
        end_time = timeout_seconds
        while end_time > 0:
            result = await self._redis.client.set(
                lock_key,
                lock_value,
                nx=True,
                ex=self._lock_expire_seconds
            )
            if result:
                return lock_value
            await asyncio.sleep(0.1)
            end_time -= 0.1
        return None

    async def _release_lock(self, lock_key: str, lock_value: str) -> bool:
        release_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        try:
            script = self._redis.client.register_script(release_script)
            result = await script(keys=[lock_key], args=[lock_value])
            return result == 1
        except Exception as e:
            return False

    async def put(self, message: Any) -> str:
        logger.debug(f"put message : {message} in [{self._stream_name}]")
        message_id = await self._redis.client.xadd(self._stream_name, {
            "data": message
        })
        return message_id

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        logger.debug(f"get message : {start_id} in [{self._stream_name}]")
        if start_id is None:
            start_id = '0'
        messages = await self._redis.client.xread(
            {
                self._stream_name: start_id
            },
            count=1,
            block=block_ms
        )
        if not messages:
            return None, None
        stream_messages = messages[0][1]
        if not stream_messages:
            return None, None
        message_id, message_data = stream_messages[0]
        try:
            return message_id, message_data.get("data")
        except Exception as e:
            logger.error(f"get message : {message_id} in [{self._stream_name}] failed : {str(e)}")
            return None, None

    async def pop(self) -> Tuple[str, Any]:
        logger.debug(f"pop message : {self._stream_name} in [{self._stream_name}]")
        lock_key = f"lock:{self._stream_name}:pop"
        lock_value = await self._acquire_lock(lock_key)
        if not lock_value:
            return None, None
        try:
            messages = await self._redis.client.xrange(self._stream_name, "-", "+", count=1)
            if not messages:
                return None, None
            message_id, message_data = messages[0]

            await self._redis.client.xdel(
                self._stream_name,
                message_id
            )

            return message_id, message_data.get("data")
        except Exception as e:
            logger.error(f"parse queue: {lock_key} in [{self._stream_name}] failed : {str(e)}")
            return None, None
        finally:
            await self._release_lock(lock_key, lock_value)

    async def clear(self) -> None:
        await self._redis.client.xtrim(self._stream_name, 0)

    async def is_empty(self) -> bool:
        return await self.size() == 0

    async def size(self) -> int:
        return await self._redis.client.xlen(self._stream_name)

    async def delete_message(self, message_id: str) -> bool:
        try:
            await self._redis.client.xdel(self._stream_name, message_id)
            return True
        except Exception as e:
            logger.error(f"delete message : {message_id} in [{self._stream_name}]")
            return False
