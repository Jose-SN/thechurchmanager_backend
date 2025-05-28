from fastapi import HTTPException, status, Depends
from typing import Optional
from your_project.schemas import OrganizationCreate, OrganizationUpdate
from your_project.services.organization_service import OrganizationService
from your_project.dependencies import get_current_user

organization_service = OrganizationService()

class OrganizationController:

    async def fetch_organization_controller(self, id: Optional[str], current_user=Depends(get_current_user)):
        try:
            data = await organization_service.get_organization_data(id)
            return data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve organization overview data: {str(e)}")

    async def fetch_organization_users_controller(self, id: Optional[str], current_user=Depends(get_current_user)):
        try:
            data = await organization_service.get_organization_users(id)
            return data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve organization users overview data: {str(e)}")

    async def insert_organization_controller(self, org: OrganizationCreate, current_user=Depends(get_current_user)):
        try:
            saved_org = await organization_service.save_organization_data(org)
            return {
                "success": True,
                "message": "Successfully added",
                "data": saved_org
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

    async def update_organization_controller(self, org: OrganizationUpdate, current_user=Depends(get_current_user)):
        try:
            await organization_service.update_organization_data(org)
            return {
                "success": True,
                "message": "Successfully updated"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    async def remove_organization_controller(self, organizationid: str, current_user=Depends(get_current_user)):
        try:
            msg = await organization_service.delete_organization_data(organizationid)
            if msg:
                raise HTTPException(status_code=404, detail=msg)
            return {
                "success": True,
                "message": "Successfully deleted"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")


organization_controller = OrganizationController()
