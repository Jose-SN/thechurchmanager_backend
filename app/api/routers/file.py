from fastapi import APIRouter, UploadFile, File as UploadFileType
from controllers import FileController

router = APIRouter(prefix="/files", tags=["Files"])
controller = FileController()

@router.get("/")
async def list_files():
    return await controller.list_files()

@router.get("/{file_id}")
async def get_file(file_id: str):
    return await controller.get_file(file_id)

@router.post("/save")
async def save_file(file_data: dict):
    return await controller.save_file(file_data)

@router.put("/{file_id}")
async def update_file(file_id: str, update_data: dict):
    return await controller.update_file(file_id, update_data)

@router.delete("/db/{file_id}")
async def delete_file_db(file_id: str):
    return await controller.delete_file_db(file_id)

@router.post("/upload")
async def upload_file(file: UploadFile = UploadFileType(...)):
    return await controller.upload_file(file)

@router.delete("/s3/{file_name}")
async def delete_file_s3(file_name: str):
    return await controller.delete_file_s3(file_name)
