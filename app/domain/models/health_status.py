from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    service: str = Field(default="", description="the service name to be health check")
    status: str = Field(default="", description="the health status, ok or error")
    details: str = Field(default="", description="the error details")
