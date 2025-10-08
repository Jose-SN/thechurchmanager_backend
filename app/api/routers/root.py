from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["Root"])

@router.get("/", response_class=HTMLResponse)
async def root():
    return "<h4 style='text-align:center;'>THE CHURCH MANAGER</h4>"

@router.get("/{full_path:path}")
async def catch_all(full_path: str):
    return RedirectResponse(url="/")
