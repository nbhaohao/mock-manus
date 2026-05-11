from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

import logging

from app.infrastructure.storage.postgres import get_postgres
from app.infrastructure.storage.redis_client import get_redis
from app.interfaces.endpoints.routes import router
from app.interfaces.errors.exception_handlers import register_exception_handlers
from core.config import get_settings
from fastapi import FastAPI

from app.infrastructure.logging import setup_logging

settings = get_settings()

print(settings)
setup_logging()
logger = logging.getLogger()

logger.info("测试")

openapi_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态检测** 等 API 接口 用于监测系统的运行状态"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MoocManus 正在初始化")

    redis = get_redis()
    await redis.init()

    postgres = get_postgres()
    await postgres.init()

    try:
        # lifespan 节点/分界
        yield
    finally:
        await redis.shutdown()
        await postgres.shutdown()
        logger.info("MoocManus 正在关闭")


app = FastAPI(
    title="MoocManus通用智能体",
    description="MoocManus 是一个通用的 AI Agent 系统",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(router, prefix="/api")
