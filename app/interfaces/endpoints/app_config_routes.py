import logging
from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends

from app.application.services.app_config_service import AppConfigService
from app.domain.models.app_config import AgentConfig, LLMConfig, MCPConfig
from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_app_config_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/app-config", tags=["设置模块"])


@router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取 LLM 配置信息",
    description="包含 LLM Provider 的 base_url, temperature, model_name, max_tokens",
)
async def get_llm_config(
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[LLMConfig]:
    llm_config = await app_config_service.get_llm_config()
    return Response.success(data=llm_config.model_dump(exclude={"api_key"}))


@router.post(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="更新 LLM 配置信息",
    description="更新 LLM 配置信息, 当 api_key 为空的时候, 表示不更新该字段",
)
async def update_llm_config(
    new_app_config: LLMConfig,
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[LLMConfig]:
    updated_llm_config = await app_config_service.update_llm_config(new_app_config)
    return Response.success(
        msg="updated_llm_config success",
        data=updated_llm_config.model_dump(exclude={"api_key"}),
    )


@router.get(
    path="/agent",
    response_model=Response[AgentConfig],
    summary="获取 Agent 配置信息",
    description="包含 agent 的 max_iterations, max_retries, max_search_results",
)
async def get_agent_config(
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[AgentConfig]:
    agent_config = await app_config_service.get_agent_config()
    return Response.success(data=agent_config.model_dump())


@router.post(
    path="/agent",
    response_model=Response[AgentConfig],
    summary="更新 agent 配置信息",
    description="更新 agent 配置信息",
)
async def update_agent_config(
    new_agent_config: AgentConfig,
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[AgentConfig]:
    updated_agent_config = await app_config_service.update_agent_config(
        new_agent_config
    )
    return Response.success(
        msg="updated_agent_config success", data=updated_agent_config.model_dump()
    )


@router.get(
    path="/mcp-servers",
    response_model=Response,
    summary="获取 MCP服务器工具列表",
    description="获取当前系统的 MCP服务器里边,包含 MCP 服务名字, 工具列表, 启用状态等",
)
async def get_mcp_servers(
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response:
    # todo:
    pass


@router.post(
    path="/mcp-servers",
    response_model=Response[Optional[Dict]],
    summary="add new MCP Server",
    description="post mcp config to add new MCP Server",
)
async def create_mcp_servers(
    mcp_config: MCPConfig,
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[Optional[Dict]]:
    await app_config_service.update_and_create_mcp_servers(mcp_config)
    return Response.success(msg="add new MCP Server success")


@router.post(
    path="/mcp-servers/{server_name}/delete",
    response_model=Response[Optional[Dict]],
    summary="delete MCP Server",
    description="delete MCP Server by server_name",
)
async def delete_mcp_server(
    server_name: str,
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[Optional[Dict]]:
    await app_config_service.delete_mcp_server(server_name)
    return Response.success(msg="delete MCP Server success")


@router.post(
    path="/mcp-servers/{server_name}/enabled",
    response_model=Response[Optional[Dict]],
    summary="update MCP Server enabled status",
    description="update MCP Server enabled status by server_name",
)
async def set_mcp_server_enabled(
    server_name: str,
    enabled: bool = Body(...),
    app_config_service: AppConfigService = Depends(get_app_config_service),
) -> Response[Optional[Dict]]:
    await app_config_service.set_mcp_server_enabled(server_name, enabled)
    return Response.success(msg="update MCP Server enabled status success")
