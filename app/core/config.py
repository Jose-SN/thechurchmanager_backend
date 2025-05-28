import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field, validator

load_dotenv()

class Settings(BaseSettings):
    PORT: int = Field(..., env='PORT')
    MONGO_URI: str = Field(..., env='MONGO_URI')
    MONGO_PROD_URI: str = Field('', env='MONGO_PROD_URI')
    MONGO_DATABASE_NAME: str = Field('', env='MONGO_DATABASE_NAME')
    JWT_SECRET: str = Field('BeTrack_JWT@2024', env='JWT_SECRET')
    JWT_EXPIRY: str = Field('30d', env='JWT_EXPIRY')
    GMAIL_USERNAME: str = Field('', env='GMAIL_USERNAME')
    GMAIL_PASS: str = Field('', env='GMAIL_PASS')

    @validator('PORT', 'MONGO_URI')
    def check_required(cls, v, field):
        if not v:
            raise ValueError(f"Environment variable {field.name} is missing")
        return v

settings = Settings()
