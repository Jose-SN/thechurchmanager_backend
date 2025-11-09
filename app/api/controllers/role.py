from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.role import RoleService
from fastapi.responses import JSONResponse

class RoleController:
    def __init__(self, role_service: RoleService):
        self.role_service = role_service

    async def fetch_role_controller(self, filters: dict = {}):
        try:
            roles = await self.role_service.get_role_data(filters)
            data = jsonable_encoder(roles)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve role data",
                "error": str(err)
            })

    async def save_role_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.role_service.save_role_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": result
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })
    async def save_bulk_role_controller(self, request: Request):
        body = await request.json()
        try:
            await self.role_service.save_bulk_role_data(body)
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


    async def update_role_controller(self, request: Request):
        body = await request.json()
        try:
            await self.role_service.update_role_data(body)
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

    async def delete_role_controller(self, role_id: str):
        try:
            await self.role_service.delete_role_data(role_id)
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

