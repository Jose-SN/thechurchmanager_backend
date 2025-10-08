from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/", summary="Health Check")
async def health_check():
    return {
        "timeZone": datetime.utcnow().isoformat(),
        "code": 200,
        "message": "success"
    }
