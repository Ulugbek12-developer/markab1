from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN_ID: int = 0
    DB_NAME: str = "smart_market.db"
    
    # New fields for Django and Bot
    DJANGO_SECRET_KEY: str = "django-insecure-default"
    DJANGO_DEBUG: bool = True
    CHANNEL_ID: str = "@markab_electronics"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra fields to prevent validation errors
    )

config = Settings()
