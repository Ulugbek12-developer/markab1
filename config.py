from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN_ID: int = 0  # User should set this in .env
    DB_NAME: str = "smart_market.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Settings()
