import asyncio
import logging
import uuid
from typing import Optional, Dict

from app.domain.external.message_queue import MessageQueue
from app.domain.external.task import Task, TaskRunner
from app.infrastructure.external.message_queue.redis_stream_message_queue import RedisStreamMessageQueue

logger = logging.getLogger(__name__)


class RedisStreamTask(Task):
    _task_registry: Dict[str, "RedisStreamTask"] = {}

    def __init__(self, task_runner: TaskRunner) -> None:
        self._task_runner = task_runner
        self._id = str(uuid.uuid4())
        self._execution_task: Optional[asyncio.Task] = None

        input_stream_name = f"task:input:{self._id}"
        output_stream_name = f"task:output:{self._id}"

        self._input_stream = RedisStreamMessageQueue(input_stream_name)
        self._output_stream = RedisStreamMessageQueue(output_stream_name)

        RedisStreamTask._task_registry[self._id] = self

    def _cleanup_registry(self):
        if self._id in self._task_registry:
            del RedisStreamTask._task_registry[self._id]
            logger.info(f"task {self._id} deleted from task registry")

    def _on_task_done(self) -> None:
        if self._task_runner:
            asyncio.create_task(self._task_runner.on_done(self))
        self._cleanup_registry()

    async def _execute_task(self) -> None:
        try:
            await self._task_runner.invoke(self)
        except asyncio.CancelledError:
            logger.info(f"task {self._id} was cancelled")
        except Exception as e:
            logger.error(f"task {self._id} failed: {str(e)}")
        finally:
            self._on_task_done()

    async def invoke(self) -> None:
        if not self.done:
            self._execution_task = asyncio.create_task(self._execute_task())
            logger.info(f"task {self._id} started")

    def cancel(self) -> bool:
        if not self.done:
            self._execution_task.cancel()
            logger.info(f"task {self._id} cancelled")

            self._cleanup_registry()
            return True
        self._cleanup_registry()
        return True

    @property
    def input_stream(self) -> MessageQueue:
        return self._input_stream

    @property
    def output_stream(self) -> MessageQueue:
        return self._output_stream

    @property
    def id(self) -> str:
        return self._id

    @property
    def done(self) -> bool:
        if self._execution_task is None:
            return True
        return self._execution_task.done()

    @classmethod
    def get(cls, task_id: str) -> Optional[Task]:
        return RedisStreamTask._task_registry.get(task_id)

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        return cls(task_runner)

    @classmethod
    async def destroy(cls) -> None:
        for task_id in RedisStreamTask._task_registry:
            task = RedisStreamTask._task_registry[task_id]
            task.cancel()

            if task._task_runner:
                await task._task_runner.destroy()
        cls._task_registry.clear()
