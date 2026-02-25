from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.rota_song import RotaSongController
from app.api.services.rota_song import RotaSongService
from app.api.dependencies import get_db

rota_song_router = APIRouter(tags=["RotaSong"])


def get_rota_song_service(db=Depends(get_db)):
    return RotaSongService(db)


def get_rota_song_controller(rota_song_service=Depends(get_rota_song_service)):
    return RotaSongController(rota_song_service)


@rota_song_router.get("/get")
async def get_rota_songs(
    rota_song_controller: RotaSongController = Depends(get_rota_song_controller),
    id: Optional[int] = Query(None, description="Rota song ID"),
    rota_id: Optional[int] = Query(None, description="Filter by rota ID (returns songs with details)"),
    song_id: Optional[int] = Query(None, description="Filter by song ID"),
):
    """Get rota_songs. Use rota_id to get all songs for a rota (includes song details)."""
    filters = {}
    if id is not None:
        filters["id"] = id
    if rota_id is not None:
        filters["rota_id"] = rota_id
    if song_id is not None:
        filters["song_id"] = song_id
    return await rota_song_controller.fetch_rota_song_controller(filters)


@rota_song_router.get("/{rota_song_id}")
async def get_rota_song_by_id(
    rota_song_id: int,
    rota_song_controller: RotaSongController = Depends(get_rota_song_controller)
):
    """Get a single rota_song by ID"""
    return await rota_song_controller.get_rota_song_by_id_controller(rota_song_id)


@rota_song_router.post("/save")
async def save_rota_song(
    request: Request,
    rota_song_controller: RotaSongController = Depends(get_rota_song_controller)
):
    """
    Add song to rota.
    Request body: { "rota_id": 1, "song_id": 1, "display_order": 0 }
    """
    return await rota_song_controller.save_rota_song_controller(request)


@rota_song_router.put("/update/{rota_song_id}")
async def update_rota_song(
    rota_song_id: int,
    request: Request,
    rota_song_controller: RotaSongController = Depends(get_rota_song_controller)
):
    """Update rota_song (e.g. change display_order)."""
    return await rota_song_controller.update_rota_song_controller(rota_song_id, request)


@rota_song_router.delete("/delete/{rota_song_id}")
async def delete_rota_song(
    rota_song_id: int,
    rota_song_controller: RotaSongController = Depends(get_rota_song_controller)
):
    """Remove song from rota."""
    return await rota_song_controller.delete_rota_song_controller(rota_song_id)
