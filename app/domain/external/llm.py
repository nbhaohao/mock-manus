from typing import List, Dict, Any, Protocol


class LLM(Protocol):
    async def invoke(self,
                     messages: List[Dict[str, Any]],
                     tools: List[Dict[str, Any]] = None,
                     response_format: Dict[str, Any] = None,
                     tool_choice: str = None,
                     ):
        ...

    @property
    def model_name(self) -> str:
        ...

    @property
    def temperature(self) -> float:
        ...

    @property
    def max_token(self) -> int:
        ...
