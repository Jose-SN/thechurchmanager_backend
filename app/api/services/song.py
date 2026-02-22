from typing import List, Optional
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.song import (
    GET_SONGS_QUERY,
    GET_SONG_BY_ID_QUERY,
    GET_SONGS_BY_ORGANIZATION_QUERY,
    GET_SONGS_BY_CREATED_BY_QUERY,
    SEARCH_SONGS_QUERY,
    INSERT_SONG_QUERY,
    UPDATE_SONG_QUERY,
    DELETE_SONG_QUERY,
)

class SongService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_song_data(self, filters: dict = {}) -> List[dict]:
        """Get song data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    song = await conn.fetchrow(GET_SONG_BY_ID_QUERY, filters["id"])
                    if song:
                        return [dependencies.convert_db_types(dict(song))]
                    return []
                elif "created_by" in filters:
                    rows = await conn.fetch(
                        GET_SONGS_BY_CREATED_BY_QUERY,
                        filters["created_by"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                elif "organization_id" in filters:
                    # Check if there are search filters
                    if any(key in filters for key in ["title", "artist", "scale", "tempo", "chords", "rhythm", "lyrics"]):
                        rows = await conn.fetch(
                            SEARCH_SONGS_QUERY,
                            filters["organization_id"],
                            filters.get("title"),
                            filters.get("artist"),
                            filters.get("scale"),
                            filters.get("tempo"),
                            filters.get("chords"),
                            filters.get("rhythm"),
                            filters.get("lyrics")
                        )
                    else:
                        rows = await conn.fetch(
                            GET_SONGS_BY_ORGANIZATION_QUERY,
                            filters["organization_id"]
                        )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                
                rows = await conn.fetch(GET_SONGS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_song_data(self, song_data: dict) -> dict:
        """Save new song"""
        try:
            async with self.db_pool.acquire() as conn:
                title = song_data.get('title', '').strip()
                artist = song_data.get('artist')
                scale = song_data.get('scale')
                tempo = song_data.get('tempo')
                chords = song_data.get('chords')
                rhythm = song_data.get('rhythm')
                lyrics = song_data.get('lyrics')
                organization_id = song_data.get('organization_id')
                created_by = song_data.get('created_by')
                
                # Validate required fields
                if not organization_id:
                    raise HTTPException(status_code=400, detail="organization_id is required")
                if not title:
                    raise HTTPException(status_code=400, detail="title is required and cannot be empty")
                
                row = await conn.fetchrow(
                    INSERT_SONG_QUERY,
                    title,
                    artist,
                    scale,
                    tempo,
                    chords,
                    rhythm,
                    lyrics,
                    organization_id,
                    created_by
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_song_data(self, song_id: str, song_data: dict, organization_id: str) -> dict:
        """Update existing song"""
        if not song_id:
            raise HTTPException(status_code=400, detail="Song ID is required")
        
        if not organization_id:
            raise HTTPException(status_code=400, detail="organization_id is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if song exists
                existing = await conn.fetchrow(GET_SONG_BY_ID_QUERY, song_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Song not found")
                
                # Verify organization ownership
                if str(existing['organization_id']) != organization_id:
                    raise HTTPException(status_code=403, detail="Not authorized to update this song")
                
                # Merge existing data with update data
                merged_data = dict(existing)
                merged_data.update(song_data)
                
                title = merged_data.get('title', '').strip()
                artist = merged_data.get('artist')
                scale = merged_data.get('scale')
                tempo = merged_data.get('tempo')
                chords = merged_data.get('chords')
                rhythm = merged_data.get('rhythm')
                lyrics = merged_data.get('lyrics')
                
                # Validate required fields
                if not title:
                    raise HTTPException(status_code=400, detail="title is required and cannot be empty")
                
                row = await conn.fetchrow(
                    UPDATE_SONG_QUERY,
                    title,
                    artist,
                    scale,
                    tempo,
                    chords,
                    rhythm,
                    lyrics,
                    song_id,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Song not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_song_data(self, song_id: str, organization_id: str) -> str:
        """Delete song"""
        if not organization_id:
            raise HTTPException(status_code=400, detail="organization_id is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if song exists and belongs to organization
                existing = await conn.fetchrow(GET_SONG_BY_ID_QUERY, song_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Song not found")
                
                if str(existing['organization_id']) != organization_id:
                    raise HTTPException(status_code=403, detail="Not authorized to delete this song")
                
                result = await conn.execute(DELETE_SONG_QUERY, song_id, organization_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Song not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
