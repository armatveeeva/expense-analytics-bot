from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./expenses.db"

    bot_token: str | None = None
    telegram_bot_token: str | None = None

    flask_secret_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    @property
    def active_bot_token(self) -> str:
        """Возвращает первый найденный токен бота"""
        return self.bot_token or self.telegram_bot_token or "YOUR_BOT_TOKEN_HERE"


settings = Settings()
