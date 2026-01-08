from fastapi import Request, dependencies
from fastapi.encoders import jsonable_encoder
from app.api.services.user import UserService
from fastapi.responses import JSONResponse
from app.api import dependencies

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def fetch_user_controller(self, filters: dict = {}):
        try:
            users = await self.user_service.get_user_data(filters)
            data = jsonable_encoder(users)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve user data",
                "error": str(err)
            })

    async def save_user_controller(self, request: Request):
        body = await request.json()
        try:
            response = await self.user_service.save_user_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": response
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })
    async def save_bulk_user_controller(self, request: Request):
        body = await request.json()
        try:
            await self.user_service.save_bulk_user_data(body)
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
    async def login_user_controller(self, request: Request):
        try:
            body = await request.json()
            email = body.get("email")
            password = body.get("password")
            result = await self.user_service.login_user_data(email, password)
            if result:
                result = dependencies.convert_objectid(result)
                result = jsonable_encoder(result)  # <-- ensures datetime is serializable
            else:
                result = {}
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Login successful",
                "data": result
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })


    async def update_user_controller(self, request: Request):
        body = await request.json()
        try:
            await self.user_service.update_user_data(body)
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

    async def delete_user_controller(self, user_id: str):
        try:
            await self.user_service.delete_user_data(user_id)
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
