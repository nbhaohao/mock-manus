from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class LLMConfig(BaseModel):
    base_url: HttpUrl = " "
    api_key: str = ""
    model_name: str = "deepseek-reasoner"
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192, ge=0)


class AgentConfig(BaseModel):
    max_iterations: int = Field(default=100, ge=0, lt=1000)
    max_retries: int = Field(default=3, ge=1, lt=10)
    max_search_results: int = Field(default=10, ge=1, lt=30)


class AppConfig(BaseModel):
    llm_config: LLMConfig
    agent_config: AgentConfig

    model_config = ConfigDict(extra="allow")
