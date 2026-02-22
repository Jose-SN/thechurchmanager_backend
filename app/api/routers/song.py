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
    id: Optional[str] = Query(None, description="Song ID"),
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    created_by: Optional[str] = Query(None, description="Creator user ID"),
    title: Optional[str] = Query(None, description="Search by title"),
    artist: Optional[str] = Query(None, description="Search by artist"),
    scale: Optional[str] = Query(None, description="Search by scale"),
    tempo: Optional[str] = Query(None, description="Search by tempo"),
    chords: Optional[str] = Query(None, description="Search by chords"),
    rhythm: Optional[str] = Query(None, description="Search by rhythm"),
    lyrics: Optional[str] = Query(None, description="Search by lyrics")
):
    """
    Get songs with optional filters.
    
    Query Parameters:
    - id: Filter by song ID
    - organization_id: Filter by organization (required for most queries)
    - created_by: Filter by creator user ID
    - title: Search in title
    - artist: Search in artist
    - scale: Search in scale
    - tempo: Search in tempo
    - chords: Search in chords
    - rhythm: Search in rhythm
    - lyrics: Search in lyrics
    """
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    if created_by:
        filters["created_by"] = created_by
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
    song_id: str,
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
    
    Request body:
    {
        "organization_id": "uuid",  // Required
        "created_by": "uuid",       // Optional: User who created the song
        "title": "Song Title",      // Required
        "artist": "Artist Name",    // Optional
        "scale": "C Major",         // Optional
        "tempo": "120 BPM",         // Optional
        "chords": "C G Am F...",    // Optional
        "rhythm": "4/4",            // Optional
        "lyrics": "Song lyrics..."  // Optional
    }
    """
    return await song_controller.save_song_controller(request)

@song_router.put("/update/{song_id}")
async def update_song(
    song_id: str,
    request: Request,
    song_controller: SongController = Depends(get_song_controller)
):
    """
    Update an existing song.
    
    Request body must include organization_id for authorization:
    {
        "organization_id": "uuid",  // Required for authorization
        "title": "Updated Title",   // Optional
        "artist": "Updated Artist", // Optional
        ... (other fields as needed)
    }
    """
    return await song_controller.update_song_controller(song_id, request)

@song_router.delete("/delete/{song_id}")
async def delete_song(
    song_id: str,
    song_controller: SongController = Depends(get_song_controller),
    organization_id: str = Query(..., description="Organization ID for authorization")
):
    """
    Delete a song.
    
    Requires organization_id query parameter for authorization.
    """
    return await song_controller.delete_song_controller(song_id, organization_id)
