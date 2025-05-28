from fastapi import APIRouter
from datetime import datetime

health_route = APIRouter()

@health_route.api_route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def health_check():
    return {
        "timeZone": datetime.utcnow().isoformat(),
        "code": 200,
        "message": "success"
    }
