from typing import Protocol, Any, Tuple


class MessageQueue(Protocol):

    async def put(self, message: Any) -> str:
        ...

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        ...

    async def pop(self) -> Tuple[str, Any]:
        ...

    async def clear(self) -> None:
        ...

    async def is_empty(self) -> bool:
        ...

    async def size(self) -> int:
        ...

    async def delete_message(self, message_id: str) -> bool:
        ...
