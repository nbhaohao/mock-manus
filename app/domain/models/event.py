from datetime import datetime
import uuid
from enum import Enum
from typing import Literal, List, Any, Union, Optional, Dict

from pydantic import BaseModel, Field

from app.domain.models.file import File
from app.domain.models.plan import Plan, Step
from app.domain.models.tool_result import ToolResult


class PlanEventStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"


class StepEventStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolEventStatus(str, Enum):
    CALLING = "calling"
    CALLED = "called"


class BaseEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal[""] = ""
    created_at: datetime = Field(default_factory=datetime.now)


class PlanEvent(BaseEvent):
    type: Literal["plan"] = "plan"
    plan: Plan
    status: PlanEventStatus = PlanEventStatus.CREATED


class TitleEvent(BaseEvent):
    type: Literal["title"] = "title"
    title: str = ""


class StepEvent(BaseEvent):
    type: Literal["step"] = "step"
    step: Step
    status: StepEventStatus = StepEventStatus.STARTED


class MessageEvent(BaseEvent):
    type: Literal["message"] = "message"
    role: Literal["user", "assistant"] = "assistant"
    message: str = ""
    attachments: List[File] = Field(default_factory=list)


class BrowserTollContent(BaseModel):
    screenshot: str


class MCPToolContent(BaseModel):
    result: Any


# todo: extend more tools
ToolContent = Union[
    BrowserTollContent,
    MCPToolContent,
]


class ToolEvent(BaseEvent):
    type: Literal["tool"] = "tool"
    tool_call_id: str
    tool_name: str
    tool_content: Optional[ToolContent] = None
    function_name: str
    function_args: Dict[str, Any]
    function_result: Optional[ToolResult] = None
    status: ToolEventStatus = ToolEventStatus.CALLING


class WaitEvent(BaseEvent):
    type: Literal["wait"] = "wait"


class ErrorEvent(BaseEvent):
    type: Literal["error"] = "error"
    error: str = ""


class DoneEvent(BaseEvent):
    type: Literal["done"] = "done"


Event = Union[
    PlanEvent,
    TitleEvent,
    StepEvent,
    MessageEvent,
    ToolEvent,
    WaitEvent,
    ErrorEvent,
    DoneEvent,
]
