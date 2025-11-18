from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.permission import PermissionService
from fastapi.responses import JSONResponse

class PermissionController:
    def __init__(self, permission_service: PermissionService):
        self.permission_service = permission_service

    async def fetch_permission_controller(self, filters: dict = {}):
        try:
            permissions = await self.permission_service.get_permission_data(filters)
            data = jsonable_encoder(permissions)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve permission data",
                "error": str(err)
            })

    async def save_permission_controller(self, request: Request):
        body = await request.json()
        try:
            await self.permission_service.save_permission_data(body)
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
    async def save_bulk_permission_controller(self, request: Request):
        body = await request.json()
        try:
            organization_id = body.get("organization_id")
            permissions = body.get("permissions", [])
            updated_permissions = await self.permission_service.save_bulk_permission_data(permissions, organization_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": updated_permissions
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })


    async def update_permission_controller(self, request: Request):
        body = await request.json()
        try:
            await self.permission_service.update_permission_data(body)
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

    async def delete_permission_controller(self, permission_id: str):
        try:
            await self.permission_service.delete_permission_data(permission_id)
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

