import asyncio
import logging
import uuid
from abc import ABC
from typing import Optional, List, AsyncGenerator, Dict, Any

from app.domain.external.json_parser import JSONParser
from app.domain.external.llm import LLM
from app.domain.models.app_config import AgentConfig
from app.domain.models.memory import Memory
from app.domain.models.message import Message
from app.domain.models.tool_result import ToolResult
from app.domain.services.tools.base import BaseTool
from app.domain.models.event import Event, ToolEvent, ToolEventStatus, ErrorEvent, MessageEvent

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = ""
    _system_prompt: str = ""
    _format: Optional[str] = None
    _retry_interval: float = 1.0
    _tool_choice: Optional[str] = None

    def __init__(self,
                 agent_config: AgentConfig,
                 llm: LLM,
                 memory: Memory,
                 json_parser: JSONParser,
                 tools: List[BaseTool]) -> None:
        self._agent_config = agent_config
        self._llm = llm
        self._memory = memory
        self._json_parser = json_parser
        self._tools = tools

    @property
    def memory(self) -> Memory:
        return self._memory

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        available_tools = []
        for tool in self._tools:
            available_tools.extend(tool.get_tools())
        return available_tools

    def _get_tool(self, tool_name: str) -> BaseTool:
        for tool in self._tools:
            if tool.has_tool(tool_name):
                return tool
        raise ValueError(f"unknown tool {tool_name} not found")

    async def _invoke_llm(self, messages: List[Dict[str, Any]], format: Optional[str] = None) -> Dict[str, Any]:
        await self._add_to_memory(messages)

        response_format = {"type": format} if format else None

        for _ in range(self._agent_config.max_retries):
            try:
                message = await self._llm.invoke(
                    messages=messages,
                    tools=self._get_available_tools(),
                    response_format=response_format,
                    tool_choice=self._tool_choice
                )

                if message.get("role") == "assistant":
                    if not message.get("content") and not message.get("tool_calls"):
                        logger.warning(f"llm replied with no content or tool calls, retrying...")
                        await self._add_to_memory([
                            {"role": "assistant", "content": ""},
                            {"role": "user", "content": "AI 无响应内容, 请继续"},
                        ])
                        await asyncio.sleep(self._retry_interval)
                        continue
                    filtered_message = {"role": "assistant", "content": message["content"]}
                    if message.get("tool_calls"):
                        filtered_message["tool_calls"] = message.get("tool_calls")[:1]
                else:
                    logger.warning(f"LLM replied with unknown role {message['role']}")
                    filtered_message = message
                await self._add_to_memory([filtered_message])
                return filtered_message
            except Exception as e:
                logger.error(f"call llm error: {str(e)}")
                await asyncio.sleep(self._retry_interval)
                continue

    async def _invoke_tool(self, tool: BaseTool, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        err = ""
        for _ in range(self._agent_config.max_retries):
            try:
                return await tool.invoke(tool_name, **arguments)
            except Exception as e:
                err = str(e)
                logger.error(f"call tool [{tool_name}] error: {str(e)}")
                await asyncio.sleep(self._retry_interval)
                continue

        return ToolResult(success=False, message=err)

    async def _add_to_memory(self, messages: List[Dict[str, Any]]) -> None:
        if self._memory.empty:
            self._memory.add_message({
                "role": "system",
                "content": self._system_prompt,
            })
        self._memory.add_messages(messages)

    async def compact_memory(self) -> None:
        self._memory.compact()

    async def roll_back(self, message: Message) -> None:
        last_message = self._memory.get_last_message()
        if (
                not last_message or
                not last_message.get("tool_calls") or
                len(last_message.get("tool_calls")) == 0
        ):
            return
        tool_call = last_message.get("tool_calls")[0]
        function_name = tool_call.get("function", {}).get("name")
        tool_call_id = tool_call.get("id")
        if function_name == "message_ask_user":
            self._memory.add_message({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "function_name": function_name,
                "content": message.model_dump_json(),
            })
        else:
            self._memory.roll_back()

    async def invoke(self, query: str, format: Optional[str] = None) -> AsyncGenerator[Event, None]:
        format = format if format else self._format

        message = await self._invoke_llm(messages=[{"role": "user", "content": query}], format=format)

        for _ in range(self._agent_config.max_iterations):
            if not message.get("tool_calls"):
                break
            tool_messages = []
            for tool_call in message["tool_calls"]:
                if not tool_call.get("function"):
                    continue
                tool_call_id = tool_call["id"] or str(uuid.uuid4())
                function_name = tool_call["function"]["name"]
                function_args = await self._json_parser.invoke(tool_call["function"]["arguments"])

                tool = self._get_tool(function_name)

                # todo tool_content
                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    status=ToolEventStatus.CALLING
                )
                result = await self._invoke_tool(tool=tool, tool_name=function_name, arguments=function_args)

                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    function_result=result,
                    status=ToolEventStatus.CALLED
                )

                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "function_name": function_name,
                    "content": result.model_dump(),
                })

            message = await self._invoke_llm(messages=tool_messages)
        else:
            yield ErrorEvent(error=f"Agent 迭代超过最大迭代次数: {self._agent_config.max_iterations}, 任务失败")
        yield MessageEvent(message=message["content"])
