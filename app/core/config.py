import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

load_dotenv('./../.env')

class Settings(BaseSettings):
    PORT: int = Field(default=8000, validation_alias='PORT')
    MONGO_URI: str = Field(default='', validation_alias='MONGO_URI')
    MONGO_PROD_URI: str = Field(default='', validation_alias='MONGO_PROD_URI')
    MONGO_DATABASE_NAME: str = Field(default='TheChurchManager', validation_alias='MONGO_DATABASE_NAME')
    JWT_SECRET: str = Field(default='BeTrack_JWT@2024', validation_alias='JWT_SECRET')
    JWT_EXPIRY: str = Field(default='30d', validation_alias='JWT_EXPIRY')
    GMAIL_USERNAME: str = Field(default='', validation_alias='GMAIL_USERNAME')
    GMAIL_PASS: str = Field(default='', validation_alias='GMAIL_PASS')

    @field_validator('PORT', 'MONGO_URI')
    @classmethod
    def check_required(cls, v, info):
        if not v:
            raise ValueError(f"Environment variable {info.field_name} is missing")
        return v
    class Config:
        env_file = ".env"
        extra = "ignore"  # <<< Add this line

settings = Settings()