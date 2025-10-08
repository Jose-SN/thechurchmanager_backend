import motor.motor_asyncio
import logging
from app.core.config import settings

client = None
db = None

async def connect_db():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_PROD_URI or settings.MONGO_URI)
        print("MongoDB client created:", settings.MONGO_DATABASE_NAME)
        db = client[settings.MONGO_DATABASE_NAME]
        logging.info("✅ Database connection achieved")
        print("✅ MongoDB connected", db)
        # print(db.name)                           # "TheChurchManager"
        # print(await client.list_database_names())
        # print(await db.list_collection_names())
        # users = db["users"] 
        # print("Users collection:", users)
        # user = await users.find().to_list()
        # print(user)
        return db
    except Exception as e:
        logging.error(f"❌ Database connection error: {e}")


def get_db():
    return db
