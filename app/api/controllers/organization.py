from fastapi import Request, dependencies
from fastapi.encoders import jsonable_encoder
from app.api.services.organization import OrganizationService
from fastapi.responses import JSONResponse
from app.api import dependencies

class OrganizationController:
    def __init__(self, organization_service: OrganizationService):
        self.organization_service = organization_service

    async def fetch_organization_controller(self, filters: dict = {}):
        try:
            organizations = await self.organization_service.get_organization_data(filters)
            data = jsonable_encoder(organizations)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve organization data",
                "error": str(err)
            })

    async def save_organization_controller(self, request: Request):
        body = await request.json()
        try:
            response = await self.organization_service.save_organization_data(body)
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
    async def save_bulk_organization_controller(self, request: Request):
        body = await request.json()
        try:
            await self.organization_service.save_bulk_organization_data(body)
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
    async def login_organization_controller(self, request: Request):
        try:
            body = await request.json()
            email = body.get("email")
            password = body.get("password")
            result = await self.organization_service.login_organization_data(email, password)
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


    async def update_organization_controller(self, request: Request):
        body = await request.json()
        try:
            await self.organization_service.update_organization_data(body)
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

    async def delete_organization_controller(self, organization_id: str):
        try:
            await self.organization_service.delete_organization_data(organization_id)
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
