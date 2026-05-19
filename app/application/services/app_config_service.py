from app.application.errors.exceptions import NotFoundError
from app.domain.models.app_config import AgentConfig, AppConfig, LLMConfig, MCPConfig
from app.domain.repositories.app_config_repository import AppConfigRepository


class AppConfigService:
    def __init__(self, app_config_repository: AppConfigRepository) -> None:
        self.app_config_repository = app_config_repository

    async def _load_app_config(self) -> AppConfig:
        return self.app_config_repository.load()

    async def get_llm_config(self) -> LLMConfig:
        app_config = await self._load_app_config()
        return app_config.llm_config

    async def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        app_config = await self._load_app_config()

        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key

        app_config.llm_config = llm_config
        self.app_config_repository.save(app_config)
        return llm_config

    async def get_agent_config(self) -> AgentConfig:
        app_config = await self._load_app_config()
        return app_config.agent_config

    async def update_agent_config(self, agent_config: AgentConfig) -> AgentConfig:
        app_config = await self._load_app_config()

        app_config.agent_config = agent_config
        self.app_config_repository.save(app_config)
        return app_config.agent_config

    async def update_and_create_mcp_servers(self, mcp_config: MCPConfig) -> MCPConfig:
        app_config = await self._load_app_config()
        app_config.mcp_config.mcpServers.update(mcp_config.mcpServers)

        self.app_config_repository.save(app_config)
        return app_config.mcp_config

    async def delete_mcp_server(self, server_name: str) -> MCPConfig:
        app_config = await self._load_app_config()

        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"Server {server_name} not found")
        del app_config.mcp_config.mcpServers[server_name]
        self.app_config_repository.save(app_config)
        return app_config.mcp_config

    async def set_mcp_server_enabled(
        self, server_name: str, enabled: bool
    ) -> MCPConfig:
        app_config = await self._load_app_config()

        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"Server {server_name} not found")
        app_config.mcp_config.mcpServers[server_name].enabled = enabled
        self.app_config_repository.save(app_config)
        return app_config.mcp_config
