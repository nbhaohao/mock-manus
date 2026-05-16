import logging
from typing import Dict, List, Any

from pydantic import BaseModel

from app.application.errors.exceptions import ServerRequestError
from app.domain.external.llm import LLM
from app.domain.models.app_config import LLMConfig
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAILLM(LLM):

    def __init__(self, llm_config: LLMConfig):
        self.client = AsyncOpenAI(
            base_url=str(llm_config.base_url),
            api_key=llm_config.api_key,
        )

        self._model_name = llm_config.model_name
        self._temperature = llm_config.temperature
        self._max_tokens = llm_config.max_tokens
        self._timeout = 3600

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    async def invoke(self,
                     messages: List[Dict[str, Any]],
                     tools: List[Dict[str, Any]] = None,
                     response_format: Dict[str, Any] = None,
                     tool_choice: str = None,
                     ) -> Dict[str, Any]:
        try:
            if tools:
                logger.info(f"call openai invoke for tools {self.model_name}")
                response = await self.client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    response_format=response_format,
                    tools=tools,
                    tool_choice=tool_choice,
                    parallel_tool_calls=False,
                    timeout=self._timeout,
                )
            else:
                logger.info(f"call openai invoke without tools {self.model_name}")
                response = await self.client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    response_format=response_format,
                    tools=tools,
                    tool_choice=tool_choice,
                    parallel_tool_calls=False,
                    timeout=self._timeout,
                )
            logger.info(f"OpenAILL return {response.model_dump()}")
            return response.choices[0].message.model_dump()
        except Exception as e:
            logger.error(f"call openai invoke failed: {str(e)}")
            raise ServerRequestError("call openai invoke failed")


if __name__ == "__main__":
    import asyncio


    async def main():
        llm = OpenAILLM(LLMConfig(
            base_url="https://api.deepseek.com",
            api_key="",
            model_name="deepseek-v4-flash",
        ))
        response = await llm.invoke(messages=[{"role": "user", "content": "Hi"}])
        print(response)


    asyncio.run(main())
