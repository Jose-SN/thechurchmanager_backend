import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings(BaseSettings):
    PORT: int = Field(default=8000, validation_alias='PORT')
    MONGO_URI: str = Field(default='', validation_alias='MONGO_URI')
    MONGO_PROD_URI: str = Field(default='', validation_alias='MONGO_PROD_URI')
    MONGO_DATABASE_NAME: str = Field(default='TheChurchManager', validation_alias='MONGO_DATABASE_NAME')
    JWT_SECRET: str = Field(default='BeTrack_JWT@2024', validation_alias='JWT_SECRET')
    JWT_EXPIRY: str = Field(default='30d', validation_alias='JWT_EXPIRY')
    GMAIL_USERNAME: str = Field(default='', validation_alias='GMAIL_USERNAME')
    GMAIL_PASS: str = Field(default='', validation_alias='GMAIL_PASS')
    
    # PostgreSQL settings
    POSTGRESQL_DB_HOST: str = Field(default='localhost', validation_alias='POSTGRESQL_DB_HOST')
    POSTGRESQL_DB_PORT: int = Field(default=5432, validation_alias='POSTGRESQL_DB_PORT')
    POSTGRESQL_DB_USER: str = Field(default='', validation_alias='POSTGRESQL_DB_USER')
    POSTGRESQL_DB_PASSWORD: str = Field(default='', validation_alias='POSTGRESQL_DB_PASSWORD')
    POSTGRESQL_DB_NAME: str = Field(default='', validation_alias='POSTGRESQL_DB_NAME')
    POSTGRESQL_SSL_MODE: str = Field(default='prefer', validation_alias='POSTGRESQL_SSL_MODE')
    POSTGRESQL_SSL_REJECT_UNAUTHORIZED: bool = Field(default=False, validation_alias='POSTGRESQL_SSL_REJECT_UNAUTHORIZED')

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    @field_validator('PORT', 'MONGO_URI')
    @classmethod
    def check_required(cls, v, info):
        if not v:
            raise ValueError(f"Environment variable {info.field_name} is missing")
        return v

settings = Settings()