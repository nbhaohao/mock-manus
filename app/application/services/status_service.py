import asyncio

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus


class StatusService:
    def __init__(self, checkers: HealthChecker) -> None:
        self._checkers = checkers

    async def check_all(self) -> list[HealthStatus]:
        results = await asyncio.gather(
            *(checker.check() for checker in self._checkers), return_exceptions=True
        )

        processed_results = []
        for res in results:
            if isinstance(res, Exception):
                processed_results.append(
                    HealthStatus(
                        service="unknown service",
                        status="error",
                        details=f"unknown error: {str(res)}",
                    )
                )
            else:
                processed_results.append(res)
        return processed_results
