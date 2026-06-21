import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from urllib.parse import urlparse, unquote

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings(BaseSettings):
    PORT: int = Field(default=8000, validation_alias='PORT')
    MONGO_URI: str = Field(default='mongodb://127.0.0.1:27017', validation_alias='MONGO_URI')
    MONGO_PROD_URI: str = Field(default='', validation_alias='MONGO_PROD_URI')
    MONGO_DATABASE_NAME: str = Field(default='TheChurchManager', validation_alias='MONGO_DATABASE_NAME')
    JWT_SECRET: str = Field(default='BeTrack_JWT@2024', validation_alias='JWT_SECRET')
    JWT_EXPIRY: str = Field(default='30d', validation_alias='JWT_EXPIRY')
    GMAIL_USERNAME: str = Field(default='', validation_alias='GMAIL_USERNAME')
    GMAIL_PASS: str = Field(default='', validation_alias='GMAIL_PASS')
    THE_CHURCH_MANAGER_APP: str = Field(default='', validation_alias='THE_CHURCH_MANAGER_APP')
    
    # Amazon SES settings
    SES_SMTP_SERVER: str = Field(default='', validation_alias='SES_SMTP_SERVER')
    SES_SMTP_PORT: int = Field(default=587, validation_alias='SES_SMTP_PORT')
    SES_SMTP_USERNAME: str = Field(default='', validation_alias='SES_SMTP_USERNAME')
    SES_SMTP_PASSWORD: str = Field(default='', validation_alias='SES_SMTP_PASSWORD')
    SES_FROM_EMAIL: str = Field(default='', validation_alias='SES_FROM_EMAIL')
    
    # PostgreSQL settings
    DATABASE_URL: str = Field(default='', validation_alias='DATABASE_URL')
    POSTGRESQL_DB_HOST: str = Field(default='localhost', validation_alias='POSTGRESQL_DB_HOST')
    POSTGRESQL_DB_PORT: int = Field(default=5432, validation_alias='POSTGRESQL_DB_PORT')
    POSTGRESQL_DB_USER: str = Field(default='', validation_alias='POSTGRESQL_DB_USER')
    POSTGRESQL_DB_PASSWORD: str = Field(default='', validation_alias='POSTGRESQL_DB_PASSWORD')
    POSTGRESQL_DB_NAME: str = Field(default='', validation_alias='POSTGRESQL_DB_NAME')
    POSTGRESQL_SSL_MODE: str = Field(default='prefer', validation_alias='POSTGRESQL_SSL_MODE')
    POSTGRESQL_SSL_REJECT_UNAUTHORIZED: bool = Field(default=False, validation_alias='POSTGRESQL_SSL_REJECT_UNAUTHORIZED')

    # IAM handled by separate service — disable local JWT gate until wired up
    IAM_AUTH_ENABLED: bool = Field(default=False, validation_alias='IAM_AUTH_ENABLED')

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    @model_validator(mode='after')
    def apply_database_url(self):
        if not self.DATABASE_URL:
            return self
        raw = self.DATABASE_URL.strip()
        for prefix in ("postgresql+asyncpg://", "postgresql+psycopg2://", "postgresql://", "postgres://"):
            if raw.startswith(prefix):
                raw = "postgresql://" + raw[len(prefix):]
                break
        parsed = urlparse(raw)
        if parsed.hostname:
            self.POSTGRESQL_DB_HOST = parsed.hostname
        if parsed.port:
            self.POSTGRESQL_DB_PORT = parsed.port
        if parsed.username:
            self.POSTGRESQL_DB_USER = unquote(parsed.username)
        if parsed.password:
            self.POSTGRESQL_DB_PASSWORD = unquote(parsed.password)
        if parsed.path and parsed.path != "/":
            self.POSTGRESQL_DB_NAME = parsed.path.lstrip("/")
        if parsed.hostname and "supabase.com" in parsed.hostname:
            self.POSTGRESQL_SSL_MODE = "require"
        return self

    def is_postgresql_configured(self) -> bool:
        if self.DATABASE_URL.strip():
            return True
        return bool(
            self.POSTGRESQL_DB_HOST
            and self.POSTGRESQL_DB_USER
            and self.POSTGRESQL_DB_PASSWORD
            and self.POSTGRESQL_DB_NAME
        )

    def get_sqlalchemy_async_url(self) -> str:
        if self.DATABASE_URL.strip():
            url = self.DATABASE_URL.strip()
            if url.startswith("postgresql+asyncpg://"):
                return url
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRESQL_DB_USER}:"
            f"{self.POSTGRESQL_DB_PASSWORD}@{self.POSTGRESQL_DB_HOST}:"
            f"{self.POSTGRESQL_DB_PORT}/{self.POSTGRESQL_DB_NAME}"
        )

    def get_sqlalchemy_sync_url(self) -> str:
        if self.DATABASE_URL.strip():
            url = self.DATABASE_URL.strip()
            if url.startswith("postgresql+psycopg2://"):
                return url
            if url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+psycopg2://", 1)
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRESQL_DB_USER}:"
            f"{self.POSTGRESQL_DB_PASSWORD}@{self.POSTGRESQL_DB_HOST}:"
            f"{self.POSTGRESQL_DB_PORT}/{self.POSTGRESQL_DB_NAME}"
        )

    def get_asyncpg_connect_kwargs(self) -> dict:
        return {
            "host": self.POSTGRESQL_DB_HOST,
            "port": self.POSTGRESQL_DB_PORT,
            "user": self.POSTGRESQL_DB_USER,
            "password": self.POSTGRESQL_DB_PASSWORD,
            "database": self.POSTGRESQL_DB_NAME,
        }

    @field_validator('PORT')
    @classmethod
    def check_port(cls, v):
        if not v:
            raise ValueError("Environment variable PORT is missing")
        return v

settings = Settings()