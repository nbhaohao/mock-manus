from typing import Optional, Protocol

from app.domain.models.app_config import AppConfig


class AppConfigRepository(Protocol):
    def load(self) -> Optional["AppConfig"]:
        ...

    def save(self, app_config: AppConfig) -> None:
        ...
