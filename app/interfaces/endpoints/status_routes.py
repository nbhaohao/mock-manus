from fastapi import APIRouter

import logging
from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response,
    summary="系统健康检查",
    description=("检查 postgres, redis, fastapi")
)
async def get_status() -> Response:
    # todo: postgres/redis
    return Response.success()
