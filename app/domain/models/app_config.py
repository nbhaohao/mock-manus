from enum import Enum
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, ConfigDict, HttpUrl, Field, model_validator


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


class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


class MCPServerConfig(BaseModel):
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP
    enabled: bool = True
    description: Optional[str] = None
    env: Optional[Dict[str, Any]] = None

    # stdio
    command: Optional[str] = None
    args: Optional[List[str]] = None

    # streamable_http, sse
    url: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_mcp_server_config(self):
        if self.transport in [MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP]:
            if not self.url:
                raise ValueError("MCP server url is required when transport is STREAMABLE_HTTP or SSE")
        if self.transport == MCPTransport.STDIO:
            if not self.command:
                raise ValueError("MCP server command is required when transport is STDIO")
        return self


class MCPConfig(BaseModel):
    mcpServers: Dict[str, MCPServerConfig] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class AppConfig(BaseModel):
    llm_config: LLMConfig
    agent_config: AgentConfig
    mcp_config: MCPConfig

    model_config = ConfigDict(extra="allow")
