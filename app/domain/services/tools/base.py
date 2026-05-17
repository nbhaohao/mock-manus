import inspect
from typing import Dict, Any, List, Callable

from app.domain.models.tool_result import ToolResult


def tool(
        name: str,
        description: str,
        parameters: Dict[str, Dict[str, Any]],
        required: List[str]
) -> Callable:
    """Open ai tool decorator"""

    def decorator(func):
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }
        func._tool_name = name
        func._tool_description = description
        func._tool_schema = tool_schema
        return func

    return decorator


class BaseTool:
    name: str = ""

    def __init__(self) -> None:
        self._tools_cache = None

    @classmethod
    def _filter_parameters(cls, method: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        filtered_kwargs = {}
        sign = inspect.signature(method)
        for key, value in kwargs.items():
            if key in sign.parameters:
                filtered_kwargs[key] = value
        return filtered_kwargs

    def get_tools(self) -> List[Dict[str, Any]]:
        if self._tools_cache is not None:
            return self._tools_cache
        tools = []

        for _, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_tool_schema"):
                tools.append(getattr(method, "_tool_schema"))
        self._tools_cache = tools
        return tools

    def has_tool(self, tool_name: str) -> bool:
        for _, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_tool_name") and getattr(method, '_tool_name') == tool_name:
                return True
        return False

    async def invoke(self, tool_name: str, **kwargs) -> ToolResult:
        for _, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_tool_name") and getattr(method, "_tool_name") == tool_name:
                filtered_kwargs = self._filter_parameters(method, kwargs)

                return await method(**filtered_kwargs)
        return ValueError(f"tool {tool_name} not found")
