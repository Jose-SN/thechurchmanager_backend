from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.user_role import UserRoleService
from fastapi.responses import JSONResponse

class UserRoleController:
    def __init__(self, user_role_service: UserRoleService):
        self.user_role_service = user_role_service

    async def fetch_user_role_controller(self, filters: dict = {}):
        try:
            user_roles = await self.user_role_service.get_user_role_data(filters)
            data = jsonable_encoder(user_roles)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve user role data",
                "error": str(err)
            })

    async def save_user_role_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.user_role_service.save_user_role_data(body)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def save_bulk_user_role_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.user_role_service.save_bulk_user_role_data(body)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def update_user_role_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.user_role_service.update_user_role_data(body)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_user_role_controller(self, user_role_id: str):
        try:
            await self.user_role_service.delete_user_role_data(user_role_id)
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

    async def update_roles_controller(self, request: Request):
        body = await request.json()
        try:
            user_id = body.get("user_id")
            organization_id = body.get("organization_id")
            roles = body.get("roles", [])
            
            if not user_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "user_id is required"
                })
            
            if not organization_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "organization_id is required"
                })
            
            result = await self.user_role_service.update_user_roles_sync(user_id, organization_id, roles)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated roles",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update roles failed",
                "error": str(err)
            })

