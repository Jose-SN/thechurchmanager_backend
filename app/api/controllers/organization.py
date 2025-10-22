from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.organization import OrganizationService
from fastapi.responses import JSONResponse

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
            await self.organization_service.save_organization_data(body)
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
        body = await request.json()
        try:
            result = await self.organization_service.login_organization_data(body.email, body.password)
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







# from fastapi import HTTPException, status, Depends
# from typing import Optional
# from schemas import OrganizationCreate, OrganizationUpdate
# from services import OrganizationService
# from utils import get_current_user

# organization_service = OrganizationService()

# class OrganizationController:

#     async def fetch_organization_controller(self, id: Optional[str], current_user=Depends(get_current_user)):
#         try:
#             data = await organization_service.get_organization_data(id)
#             return data
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Failed to retrieve organization overview data: {str(e)}")

#     async def fetch_organization_users_controller(self, id: Optional[str], current_user=Depends(get_current_user)):
#         try:
#             data = await organization_service.get_organization_users(id)
#             return data
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Failed to retrieve organization users overview data: {str(e)}")

#     async def insert_organization_controller(self, org: OrganizationCreate, current_user=Depends(get_current_user)):
#         try:
#             saved_org = await organization_service.save_organization_data(org)
#             return {
#                 "success": True,
#                 "message": "Successfully added",
#                 "data": saved_org
#             }
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

#     async def update_organization_controller(self, org: OrganizationUpdate, current_user=Depends(get_current_user)):
#         try:
#             await organization_service.update_organization_data(org)
#             return {
#                 "success": True,
#                 "message": "Successfully updated"
#             }
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

#     async def remove_organization_controller(self, organizationid: str, current_user=Depends(get_current_user)):
#         try:
#             msg = await organization_service.delete_organization_data(organizationid)
#             if msg:
#                 raise HTTPException(status_code=404, detail=msg)
#             return {
#                 "success": True,
#                 "message": "Successfully deleted"
#             }
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")


# organization_controller = OrganizationController()
