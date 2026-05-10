import logging
from core.config import get_settings
from fastapi import FastAPI

from app.infrastructure.logging import setup_logging

settings = get_settings()

print(settings)
setup_logging()
logger = logging.getLogger()

logger.info("测试")
app = FastAPI()
