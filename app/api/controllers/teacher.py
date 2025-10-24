from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.teacher import TeacherService
from fastapi.responses import JSONResponse

class TeacherController:
    def __init__(self, teacher_service: TeacherService):
        self.teacher_service = teacher_service

    async def fetch_teacher_controller(self, filters: dict = {}):
        try:
            teachers = await self.teacher_service.get_teacher_data(filters)
            data = jsonable_encoder(teachers)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve teacher data",
                "error": str(err)
            })

    async def save_teacher_controller(self, request: Request):
        body = await request.json()
        try:
            await self.teacher_service.save_teacher_data(body)
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
    async def save_bulk_teacher_controller(self, request: Request):
        body = await request.json()
        try:
            await self.teacher_service.save_bulk_teacher_data(body)
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


    async def update_teacher_controller(self, request: Request):
        body = await request.json()
        try:
            await self.teacher_service.update_teacher_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_teacher_controller(self, teacher_id: str):
        try:
            await self.teacher_service.delete_teacher_data(teacher_id)
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

