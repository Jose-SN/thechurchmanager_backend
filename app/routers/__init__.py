from fastapi import APIRouter
# Root route returning simple HTML response
from fastapi.responses import HTMLResponse, RedirectResponse
from . import (
    user,
    file,
    status,
    event,
    mail_template,
    meeting,
    attendance,
    checkout,
    webhook,
    dashboard,
    organization,
    guest,
    health_check
)

router = APIRouter()

router.include_router(health_check.router, prefix="/health-check")

# Add your other routers similarly
router.include_router(user.router, prefix="/user")
router.include_router(file.router, prefix="/file")
router.include_router(status.router, prefix="/status")
router.include_router(event.router, prefix="/event")
router.include_router(mail_template.router, prefix="/mail-template")
router.include_router(meeting.router, prefix="/meeting")
router.include_router(attendance.router, prefix="/attendance")
router.include_router(checkout.router, prefix="/checkout")
router.include_router(webhook.router, prefix="/webhook")
router.include_router(dashboard.router, prefix="/dashboard")
router.include_router(organization.router, prefix="/organization")
router.include_router(guest.router, prefix="/guest")

@router.get("/", response_class=HTMLResponse)
async def root():
    app_name = "The Church Manager"  # You can load this from config or env
    return f"<h4 style='display: flex; justify-content: center; letter-spacing: 0.4;'>{app_name.upper()}</h4>"

@router.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Redirect all other paths to root
    return RedirectResponse(url="/")
