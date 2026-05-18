import logging
from typing import AsyncGenerator

from models.file import File
from models.message import Message
from models.plan import Plan, Step, ExecutionStatus
from models.event import Event, StepEventStatus, StepEvent, ToolEvent, MessageEvent, ErrorEvent, ToolEventStatus, \
    WaitEvent
from services.agents.base import BaseAgent
from app.domain.services.prompt.system import SYSTEM_PROMPT
from services.prompt.react import EXECUTION_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    name: str = "react"
    _system_prompt: str = SYSTEM_PROMPT
    _format: str = "json_object"

    async def execute_step(self, plan: Plan, step: Step, message: Message) -> AsyncGenerator[Event, None]:
        query = EXECUTION_PROMPT.format(
            message=message.message,
            attachments="\n".join(message.attachments),
            language=plan.language,
            step=step.description,
        )

        step.status = ExecutionStatus.RUNNING
        yield StepEvent(step=step, status=StepEventStatus.STARTED)

        async for event in self.invoke(query):
            if isinstance(event, ToolEvent):
                if event.function_name == "message_ask_user":
                    if event.status == ToolEventStatus.CALLING:
                        yield MessageEvent(
                            role="assistant",
                            # todo implement it later
                            message=event.function_args.get("text", "")
                        )
                    elif event.status == ToolEventStatus.CALLED:
                        yield WaitEvent()
                        return
                    continue
            elif isinstance(event, MessageEvent):
                step.status = ExecutionStatus.COMPLETED
                parsed_obj = await self._json_parser.invoke(event.message)
                new_step = Step.model_validate(parsed_obj)

                step.success = new_step.success
                step.result = new_step.result
                step.attachments = new_step.attachments

                yield StepEvent(step=step, status=StepEventStatus.COMPLETED)

                if step.result:
                    yield MessageEvent(
                        role="assistant",
                        message=step.result
                    )
                continue
            elif isinstance(event, ErrorEvent):
                step.status = ExecutionStatus.FAILED
                step.error = event.error

                yield StepEvent(step=step, status=StepEventStatus.FAILED)

            yield event

        step.status = ExecutionStatus.COMPLETED

    async def summarize(self) -> AsyncGenerator[Event, None]:
        query = SUMMARIZE_PROMPT

        async for event in self.invoke(query):
            if isinstance(event, MessageEvent):
                logger.info(f"react agent generated summary: {event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                message = Message.model_validate(parsed_obj)
                attachments = [File(filepath=filepath) for filepath in message.attachments]
                yield MessageEvent(
                    role="assistant",
                    message=message.message,
                    attachments=attachments
                )
            else: 
                yield event
