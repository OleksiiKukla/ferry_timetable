from typing import Any, Dict

from pydantic import BaseSettings, PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DB_NAME_TEST: str

    REDIS_HOST: str
    REDIS_PORT: str

    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    SQLALCHEMY_TEST_DATABASE_URI: PostgresDsn | None = None

    REDIS_URI: RedisDsn | None = None

    TELEGRAM_API_TOKEN: str
    WEBHOOK_URL: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    @validator("REDIS_URI", pre=True)
    def redis_connection(cls, c: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(c, str):
            return c
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
        )

    @validator("SQLALCHEMY_TEST_DATABASE_URI", pre=True)
    def assemble_test_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('DB_NAME_TEST')}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
