import motor.motor_asyncio
import logging
from app.core.config import settings

client = None
db = None

async def connect_db():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_PROD_URI or settings.MONGO_URI)
        db = client[settings.MONGO_DATABASE_NAME]
        logging.info("✅ Database connection achieved")
        print("✅ MongoDB connected")
        return db
    except Exception as e:
        logging.error(f"❌ Database connection error: {e}")


def get_db():
    return db
