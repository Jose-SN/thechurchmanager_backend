from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional
from app.api.controllers import AccountController
from app.api.services import AccountService
from app.api.dependencies import get_db

account_router = APIRouter(tags=["Account"])

def get_account_service(db=Depends(get_db)):
    return AccountService(db)

def get_account_controller(account_service=Depends(get_account_service)):
    return AccountController(account_service)

@account_router.post("/save", status_code=201)
async def save_account(request: Request, account_controller: AccountController = Depends(get_account_controller)):
    """Create a new account entry."""
    return await account_controller.save_account_controller(request)

@account_router.get("/get")
async def get_accounts(
    organization_id: str = Query(..., description="Organization ID (required)"),
    account_controller: AccountController = Depends(get_account_controller)
):
    """Get list of accounts filtered by organization_id."""
    filters = {"organization_id": organization_id}
    return await account_controller.fetch_account_controller(filters)

@account_router.put("/update/{account_id}")
async def update_account(
    account_id: str,
    request: Request,
    account_controller: AccountController = Depends(get_account_controller)
):
    """Update an existing account entry."""
    return await account_controller.update_account_controller(account_id, request)

@account_router.delete("/delete/{account_id}")
async def delete_account(
    account_id: str,
    account_controller: AccountController = Depends(get_account_controller)
):
    """Delete an account entry."""
    return await account_controller.delete_account_controller(account_id)

