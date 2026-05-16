from abc import ABC, abstractmethod
from typing import Protocol, Optional

from app.domain.external.message_queue import MessageQueue


class TaskRunner(ABC):

    @abstractmethod
    async def invoke(self, task: "Task") -> None:
        raise NotImplementedError

    @abstractmethod
    async def destroy(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_done(self, task: "Task") -> None:
        raise NotImplementedError


class Task(Protocol):
    async def run(self) -> None:
        ...

    async def cancel(self) -> None:
        ...

    @property
    def input_stream(self) -> MessageQueue:
        ...

    @property
    def output_stream(self) -> MessageQueue:
        ...

    @property
    def id(self) -> str:
        ...

    @property
    def done(self) -> bool:
        ...

    @classmethod
    def get(cls, task_id: str) -> Optional["Task"]:
        ...

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        ...

    @classmethod
    def destroy(cls) -> None:
        ...
