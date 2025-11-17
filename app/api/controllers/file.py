from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.file import FileService
from fastapi.responses import JSONResponse

class FileController:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    async def fetch_file_controller(self, filters: dict = {}):
        try:
            files = await self.file_service.get_file_data(filters)
            data = jsonable_encoder(files)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve file data",
                "error": str(err)
            })

    async def save_file_controller(self, request: Request):
        body = await request.json()
        try:
            await self.file_service.save_file_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": body
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def save_bulk_file_controller(self, request: Request):
        body = await request.json()
        try:
            organization_id = body.get("organization_id")
            files = body.get("files", [])
            updated_files = await self.file_service.save_bulk_file_data(files, organization_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": updated_files
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def update_file_controller(self, request: Request):
        body = await request.json()
        try:
            updated_file = await self.file_service.update_file_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated",
                "data": updated_file
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_file_controller(self, file_id: str):
        try:
            await self.file_service.delete_file_data(file_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully deleted"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Delete failed",
                "error": str(err)
            })

