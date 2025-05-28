from fastapi import HTTPException
from service import DashboardService

service = DashboardService()

class DashboardController:
    async def fetch_dashboard(self, user_id: str = ""):
        data = await service.get_dashboard_data(user_id)
        if "message" in data and data["message"] == "Internal Server Error":
            raise HTTPException(status_code=500, detail="Failed to retrieve dashboard overview data")
        return data
