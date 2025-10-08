import boto3
from bson import ObjectId
from models.file import File
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

s3 = boto3.client(
    "s3",
    aws_access_key_id="YOUR_KEY",
    aws_secret_access_key="YOUR_SECRET",
    region_name="YOUR_REGION"
)

class FileService:
    async def init_db(self):
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await init_beanie(database=client.mydatabase, document_models=[File])

    async def get_all_files(self):
        return await File.find_all().to_list()

    async def get_file_by_id(self, file_id: str):
        return await File.get(ObjectId(file_id))

    async def save_file(self, file_data: dict):
        file = File(**file_data)
        await file.insert()
        return file

    async def update_file(self, file_id: str, update_data: dict):
        file = await File.get(ObjectId(file_id))
        if file:
            await file.set(update_data)
            return file
        return None

    async def delete_file(self, file_id: str):
        file = await File.get(ObjectId(file_id))
        if file:
            await file.delete()
            return True
        return False

    def upload_to_s3(self, file_bytes, file_name, content_type):
        bucket = "YOUR_BUCKET_NAME"
        key = f"thechurchmanager-uploads/{file_name}"
        s3.put_object(Bucket=bucket, Key=key, Body=file_bytes, ContentType=content_type)
        return f"https://{bucket}.s3.amazonaws.com/{key}"

    def delete_from_s3(self, file_name):
        bucket = "YOUR_BUCKET_NAME"
        key = f"thechurchmanager-uploads/{file_name}"
        s3.delete_object(Bucket=bucket, Key=key)
        return True
