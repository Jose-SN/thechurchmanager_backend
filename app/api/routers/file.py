from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import FileController
from app.api.services import FileService
from app.api.dependencies import get_db

file_router = APIRouter(tags=["File"])

def get_file_service(db=Depends(get_db)):
    return FileService(db)

def get_file_controller(file_service=Depends(get_file_service)):
    return FileController(file_service)

@file_router.get("/get")
async def get_all_files(file_controller: FileController = Depends(get_file_controller),
    _id: str = Query(None)):
    filters = {}
    if _id:
        filters["_id"] = _id
    return await file_controller.fetch_file_controller(filters)

@file_router.post("/save")
async def save_file(request: Request, file_controller: FileController = Depends(get_file_controller)):
    return await file_controller.save_file_controller(request)

@file_router.post("/bulk-save")
async def save_bulk_file(request: Request, file_controller: FileController = Depends(get_file_controller)):
    return await file_controller.save_bulk_file_controller(request)

@file_router.put("/update")
async def update_file(request: Request, file_controller: FileController = Depends(get_file_controller)):
    return await file_controller.update_file_controller(request)

@file_router.delete("/delete/{file_id}")
async def delete_file(file_id: str, file_controller: FileController = Depends(get_file_controller)):
    return await file_controller.delete_file_controller(file_id)