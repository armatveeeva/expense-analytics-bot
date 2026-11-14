from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./expenses.db"
    bot_token: str | None = None
    telegram_bot_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    @property
    def active_bot_token(self) -> str:
        token = self.bot_token or self.telegram_bot_token
        if not token:
            raise ValueError("BOT_TOKEN не задан в .env")
        return token


settings = Settings()
