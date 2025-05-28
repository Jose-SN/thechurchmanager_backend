from fastapi import UploadFile, HTTPException
from services.file_service import FileService

service = FileService()

class FileController:
    async def list_files(self):
        files = await service.get_all_files()
        if not files:
            raise HTTPException(status_code=404, detail="No files found")
        return files

    async def get_file(self, file_id: str):
        file = await service.get_file_by_id(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file

    async def save_file(self, file_data: dict):
        return await service.save_file(file_data)

    async def update_file(self, file_id: str, update_data: dict):
        updated = await service.update_file(file_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="File not found")
        return updated

    async def delete_file_db(self, file_id: str):
        deleted = await service.delete_file(file_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted from DB"}

    async def upload_file(self, file: UploadFile):
        content = await file.read()
        s3_url = service.upload_to_s3(content, file.filename, file.content_type)
        return {"message": "File uploaded", "url": s3_url}

    async def delete_file_s3(self, file_name: str):
        service.delete_from_s3(file_name)
        return {"message": "File deleted from S3"}
