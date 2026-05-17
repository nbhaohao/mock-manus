import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Memory(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def get_message_role(self, message: Dict[str, Any]) -> str:
        return message.get("role")

    def add_message(self, message: Dict[str, Any]) -> None:
        self.messages.append(message)

    def add_messages(self, messages: List[Dict[str, Any]]) -> None:
        self.messages.extend(messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        return self.messages[-1] if len(self.messages) > 0 else None

    def roll_back(self) -> None:
        self.messages = self.messages[:-1]

    def compact(self) -> None:
        for message in self.messages:
            if self.get_message_role(message) == "tool":
                # todo: a placeholder of function name
                if message.get("function_name") in []:
                    # todo: placeholder of tool-call result
                    message["content"] = "(removed)"
                    logger.debug(f"Removed function: {message['function_name']} from memory")

    @property
    def empty(self) -> bool:
        return len(self.messages) == 0
