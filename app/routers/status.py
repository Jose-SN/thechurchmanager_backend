from fastapi import APIRouter, Depends
from controller import (
    fetch_status,
    fetch_status_overview,
    insert_status,
    update_status,
    remove_status,
)
from utils import get_current_user, validate_schema  # your auth & validation dependencies

status_router = APIRouter(prefix="/status", tags=["Status"])

# GET /status/get - Get all statuses
status_router.get("/get", dependencies=[Depends(get_current_user)])(fetch_status)

# GET /status/get-overview - Get status overview
status_router.get("/get-overview", dependencies=[Depends(get_current_user)])(fetch_status_overview)

# POST /status/save - Save a new status
status_router.post(
    "/save",
    dependencies=[Depends(get_current_user), Depends(validate_schema)]
)(insert_status)

# PUT /status/update - Update a status
status_router.put(
    "/update",
    dependencies=[Depends(get_current_user), Depends(validate_schema)]
)(update_status)

# DELETE /status/delete/{statusid} - Delete a status
status_router.delete(
    "/delete/{statusid}",
    dependencies=[Depends(get_current_user), Depends(validate_schema)]
)(remove_status)
