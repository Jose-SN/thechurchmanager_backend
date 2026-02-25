from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.song import SongController
from app.api.services.song import SongService
from app.api.dependencies import get_db

song_router = APIRouter(tags=["Song"])


def get_song_service(db=Depends(get_db)):
    return SongService(db)


def get_song_controller(song_service=Depends(get_song_service)):
    return SongController(song_service)


@song_router.get("/get")
async def get_songs(
    song_controller: SongController = Depends(get_song_controller),
    id: Optional[int] = Query(None, description="Song ID"),
    organization_id: Optional[int] = Query(None, description="Organization ID"),
    title: Optional[str] = Query(None, description="Search by title"),
    artist: Optional[str] = Query(None, description="Search by artist"),
    scale: Optional[str] = Query(None, description="Search by scale"),
    tempo: Optional[str] = Query(None, description="Search by tempo"),
    chords: Optional[str] = Query(None, description="Search by chords"),
    rhythm: Optional[str] = Query(None, description="Search by rhythm"),
    lyrics: Optional[str] = Query(None, description="Search by lyrics"),
):
    """
    Get songs with optional filters.
    """
    filters = {}
    if id is not None:
        filters["id"] = id
    if organization_id is not None:
        filters["organization_id"] = organization_id
    if title:
        filters["title"] = title
    if artist:
        filters["artist"] = artist
    if scale:
        filters["scale"] = scale
    if tempo:
        filters["tempo"] = tempo
    if chords:
        filters["chords"] = chords
    if rhythm:
        filters["rhythm"] = rhythm
    if lyrics:
        filters["lyrics"] = lyrics

    return await song_controller.fetch_song_controller(filters)


@song_router.get("/{song_id}")
async def get_song_by_id(
    song_id: int,
    song_controller: SongController = Depends(get_song_controller)
):
    """Get a single song by ID"""
    return await song_controller.get_song_by_id_controller(song_id)


@song_router.post("/save")
async def save_song(
    request: Request,
    song_controller: SongController = Depends(get_song_controller)
):
    """
    Create a new song.
    Request body: { "organization_id": 1, "title": "Song Title", "artist": "...", ... }
    """
    return await song_controller.save_song_controller(request)


@song_router.put("/update/{song_id}")
async def update_song(
    song_id: int,
    request: Request,
    song_controller: SongController = Depends(get_song_controller)
):
    """
    Update an existing song.
    Request body must include organization_id.
    """
    return await song_controller.update_song_controller(song_id, request)


@song_router.delete("/delete/{song_id}")
async def delete_song(
    song_id: int,
    song_controller: SongController = Depends(get_song_controller),
    organization_id: int = Query(..., description="Organization ID for authorization")
):
    """Delete a song. Requires organization_id query parameter."""
    return await song_controller.delete_song_controller(song_id, organization_id)
