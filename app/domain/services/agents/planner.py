import logging
from typing import Optional, AsyncGenerator

from models.event import PlanEventStatus
from models.plan import Plan, Step
from .base import BaseAgent
from ..prompt.planner import PLANNER_SYSTEM_PROMPT, CREATE_PLAN_PROMPT, UPDATE_PLAN_PROMPT
from ..prompt.system import SYSTEM_PROMPT
from ...models.message import Message
from ...models.event import Event, MessageEvent, PlanEvent

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    name: str = "planner"
    _system_prompt: str = SYSTEM_PROMPT + PLANNER_SYSTEM_PROMPT
    _format: Optional[str] = "json_object"
    _tool_choice: Optional[str] = "none"

    async def create_plan(self, message: Message) -> AsyncGenerator[Event, None]:
        query = CREATE_PLAN_PROMPT.format(
            message=message,
            attachments="\n".join(message.attachments),
        )
        async for event in self.invoke(query):
            if isinstance(event, MessageEvent):
                logger.info(f"Planner Agent generated message: {message.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                plan = Plan.model_validate(parsed_obj)

                yield PlanEvent(plan=plan, status=PlanEventStatus.CREATED)
            else:
                yield event

    async def update_plan(self, plan: Plan, step: Step) -> AsyncGenerator[Event, None]:
        query = UPDATE_PLAN_PROMPT.format(
            plan=plan.model_dump_json(),
            step=step.model_dump_json(),
        )
        async for event in self.invoke(query):
            if isinstance(event, MessageEvent):
                logger.info(f"Planner Agent updated message: {event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)
                updated_plan = Plan.model_validate(parsed_obj)

                new_steps = [Step.model_validate(step) for step in updated_plan.steps]

                first_pending_index = None
                for idx, step in enumerate(plan.steps):
                    if not step.done:
                        first_pending_index = idx
                        break
                if first_pending_index is not None:
                    updated_steps = plan.steps[:first_pending_index]
                    updated_steps.extend(new_steps)

                    plan.steps = updated_steps
                yield PlanEvent(plan=plan, status=PlanEventStatus.UPDATED)
            else:
                yield event
