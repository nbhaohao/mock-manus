from typing import List

from fastapi import APIRouter, Depends

import logging

from app.application.services.status_service import StatusService
from app.domain.models.health_status import HealthStatus
from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_status_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response[List[HealthStatus]],
    summary="系统健康检查",
    description=("检查 postgres, redis, fastapi")
)
async def get_status(
        status_service: StatusService = Depends(get_status_service),
) -> Response:
    statues = await status_service.check_all()

    if any(item.status == "error" for item in statues):
        return Response.fail(code=503, msg="system has internal errors", data=statues)

    return Response.success(msg="system health checked successfully", data=statues)
