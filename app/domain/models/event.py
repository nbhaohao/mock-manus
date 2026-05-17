from datetime import datetime
import uuid
from enum import Enum
from typing import Literal, List, Any, Union

from pydantic import BaseModel, Field

from app.domain.models.plan import Plan, Step


class PlanEventStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"


class StepEventStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


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
    # todo to implement attachments structure
    attachments: List[Any] = Field(default_factory=list)


class ToolEvent(BaseEvent):
    # todo: develop after integrates tool module.
    type: Literal["tool"] = "tool"


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
