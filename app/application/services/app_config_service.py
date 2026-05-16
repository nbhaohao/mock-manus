from app.domain.models.app_config import AppConfig, LLMConfig
from app.domain.repositories.app_config_repository import AppConfigRepository


class AppConfigService:
    def __init__(self, app_config_repository: AppConfigRepository) -> None:
        self.app_config_repository = app_config_repository

    def _load_app_config(self) -> AppConfig:
        return self.app_config_repository.load()

    def get_llm_config(self) -> LLMConfig:
        return self._load_app_config().llm_config

    def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        app_config = self._load_app_config()

        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key

        app_config.llm_config = llm_config
        self.app_config_repository.save(app_config)
        return llm_config
