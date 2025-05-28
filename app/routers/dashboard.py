from fastapi import APIRouter, Query
from .event import DashboardController

router = APIRouter()
controller = DashboardController()

@router.get("/get")
async def get_dashboard(userId: str = Query(default="", description="User ID")):
    return await controller.fetch_dashboard(userId)
