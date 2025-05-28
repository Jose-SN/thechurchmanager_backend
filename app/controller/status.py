from fastapi import HTTPException, Depends, Query, Path
from typing import Optional

from schemas.status import StatusCreate, StatusUpdate
from service import StatusService
from utils import get_current_user

# Instantiate your service
service = StatusService()


async def fetch_status(
    id: Optional[str] = Query(None),
    createdBy: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user)
):
    try:
        data = await service.get_status_data(status_id=id, created_by=createdBy)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve status overview data: {str(e)}")

async def fetch_status_overview(current_user: str = Depends(get_current_user)):
    try:
        data = await service.get_status_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve status data: {str(e)}")

async def insert_status(status: StatusCreate, current_user: str = Depends(get_current_user)):
    try:
        created_status = await service.save_status_data(status)
        return {
            "success": True,
            "message": "Successfully added",
            "data": created_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

async def update_status(status: StatusUpdate, current_user: str = Depends(get_current_user)):
    try:
        updated_status = await service.update_status_data(status)
        if not updated_status:
            raise HTTPException(status_code=404, detail="Update failed: Status not found")
        return {"success": True, "message": "Successfully updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

async def remove_status(
    statusid: str = Path(..., description="ID of the status to delete"),
    current_user: str = Depends(get_current_user)
):
    try:
        result = await service.delete_status_data(statusid)
        if result != "":
            raise HTTPException(status_code=404, detail=f"Delete failed: {result}")
        return {"success": True, "message": "Successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")
