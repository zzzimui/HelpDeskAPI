import secrets
from typing import Literal
from pydantic import (
    EmailStr, 
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator
)

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )

    DATABASE_URL: str
    API_PREFIX: str = "/api/v1"

    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    REFRESH_SECRET_KEY: str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SELECTED_DATABASE: Literal["postgres", "sqlite"] = "sqlite" # 

    # Database initialization user
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    PASSWORD_TEST_USER: str = "changethis"

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _use_psycopg_driver(cls, value: str | PostgresDsn) -> str:
        database_url = str(value)
        for scheme in ("postgres://", "postgresql://"):
            if database_url.startswith(scheme):
                return database_url.replace(scheme, "postgresql+psycopg://", 1)
        return database_url

    # @computed_field  # type: ignore[prop-decorator]
    # @property
    # def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
    #     return PostgresDsn.build(
    #         scheme="postgresql+psycopg",
    #         username=self.POSTGRES_USER,
    #         password=self.POSTGRES_PASSWORD,
    #         host=self.POSTGRES_SERVER,
    #         port=self.POSTGRES_PORT,
    #         path=self.POSTGRES_DB,
    #     )


settings = Settings()