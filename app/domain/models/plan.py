import uuid
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    success: bool = False
    attachments: List[str] = Field(default_factory=list)

    @property
    def done(self) -> bool:
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]


class Plan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    goal: str = ""
    language: str = ""
    steps: List[Any] = Field(default_factory=list)
    message: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    error: Optional[str] = None

    # todo: no result field for now.

    @property
    def done(self) -> bool:
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]

    def get_next_step(self) -> Optional[Step]:
        return next((step for step in self.steps if not step.done), None)
