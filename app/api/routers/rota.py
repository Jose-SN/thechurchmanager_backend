from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.rota import RotaController
from app.api.services.rota import RotaService
from app.api.dependencies import get_db

rota_router = APIRouter(tags=["Rota"])


def get_rota_service(db=Depends(get_db)):
    return RotaService(db)


def get_rota_controller(rota_service=Depends(get_rota_service)):
    return RotaController(rota_service)


@rota_router.get("/get")
async def get_rotas(
    rota_controller: RotaController = Depends(get_rota_controller),
    id: Optional[int] = Query(None, description="Rota ID"),
    organization_id: Optional[int] = Query(None, description="Organization ID"),
    team_id: Optional[int] = Query(None, description="Team ID"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    service_type: Optional[str] = Query(None, description="Search by service type"),
):
    """Get rotas with optional filters."""
    filters = {}
    if id is not None:
        filters["id"] = id
    if organization_id is not None:
        filters["organization_id"] = organization_id
    if team_id is not None:
        filters["team_id"] = team_id
    if date:
        filters["date"] = date
    if service_type:
        filters["service_type"] = service_type

    return await rota_controller.fetch_rota_controller(filters)


@rota_router.get("/{rota_id}")
async def get_rota_by_id(
    rota_id: int,
    rota_controller: RotaController = Depends(get_rota_controller)
):
    """Get a single rota by ID"""
    return await rota_controller.get_rota_by_id_controller(rota_id)


@rota_router.post("/save")
async def save_rota(
    request: Request,
    rota_controller: RotaController = Depends(get_rota_controller)
):
    """
    Create a new rota.
    Request body: { "date": "2024-01-15T09:00:00", "team_id": 1, "organization_id": 1, ... }
    """
    return await rota_controller.save_rota_controller(request)


@rota_router.put("/update/{rota_id}")
async def update_rota(
    rota_id: int,
    request: Request,
    rota_controller: RotaController = Depends(get_rota_controller)
):
    """Update an existing rota. Request body must include organization_id."""
    return await rota_controller.update_rota_controller(rota_id, request)


@rota_router.delete("/delete/{rota_id}")
async def delete_rota(
    rota_id: int,
    rota_controller: RotaController = Depends(get_rota_controller),
    organization_id: int = Query(..., description="Organization ID for authorization")
):
    """Delete a rota. Requires organization_id query parameter."""
    return await rota_controller.delete_rota_controller(rota_id, organization_id)
