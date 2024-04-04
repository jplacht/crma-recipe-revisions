from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class SettingModel(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )

    PATH_REVISIONS: str = "revisions"
    PATH_RECIPES: str = "recipes"


settings = SettingModel()
