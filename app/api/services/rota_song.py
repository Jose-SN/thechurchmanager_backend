from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.rota_song import (
    GET_ROTA_SONGS_QUERY,
    GET_ROTA_SONG_BY_ID_QUERY,
    GET_ROTA_SONGS_BY_ROTA_QUERY,
    GET_ROTA_SONGS_BY_SONG_QUERY,
    INSERT_ROTA_SONG_QUERY,
    UPDATE_ROTA_SONG_QUERY,
    DELETE_ROTA_SONG_QUERY,
)


class RotaSongService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_rota_song_data(self, filters: dict = None) -> List[dict]:
        """Get rota_song data with filtering"""
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_ROTA_SONG_BY_ID_QUERY, filters["id"])
                    if row:
                        return [dependencies.convert_db_types(dict(row))]
                    return []
                elif "rota_id" in filters:
                    rows = await conn.fetch(
                        GET_ROTA_SONGS_BY_ROTA_QUERY,
                        filters["rota_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                elif "song_id" in filters:
                    rows = await conn.fetch(
                        GET_ROTA_SONGS_BY_SONG_QUERY,
                        filters["song_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]

                rows = await conn.fetch(GET_ROTA_SONGS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching rota_song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_rota_song_data(self, data: dict) -> dict:
        """Add song to rota"""
        try:
            async with self.db_pool.acquire() as conn:
                rota_id = data.get('rota_id')
                song_id = data.get('song_id')
                display_order = data.get('display_order', 0)

                if not rota_id:
                    raise HTTPException(status_code=400, detail="rota_id is required")
                if not song_id:
                    raise HTTPException(status_code=400, detail="song_id is required")

                try:
                    rota_id = int(rota_id)
                    song_id = int(song_id)
                    display_order = int(display_order) if display_order is not None else 0
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="rota_id and song_id must be valid integers")

                row = await conn.fetchrow(
                    INSERT_ROTA_SONG_QUERY,
                    rota_id,
                    song_id,
                    display_order
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving rota_song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_rota_song_data(self, rota_song_id: int, data: dict) -> dict:
        """Update rota_song record"""
        if rota_song_id is None:
            raise HTTPException(status_code=400, detail="Rota song ID is required")

        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_ROTA_SONG_BY_ID_QUERY, rota_song_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Rota song not found")

                merged = dict(existing)
                merged.update(data)

                rota_id = merged.get('rota_id')
                song_id = merged.get('song_id')
                display_order = merged.get('display_order', 0)

                if not rota_id or not song_id:
                    raise HTTPException(status_code=400, detail="rota_id and song_id are required")

                try:
                    rota_id = int(rota_id)
                    song_id = int(song_id)
                    display_order = int(display_order) if display_order is not None else 0
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="rota_id and song_id must be valid integers")

                row = await conn.fetchrow(
                    UPDATE_ROTA_SONG_QUERY,
                    rota_id,
                    song_id,
                    display_order,
                    rota_song_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Rota song not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating rota_song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_rota_song_data(self, rota_song_id: int) -> str:
        """Remove song from rota"""
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_ROTA_SONG_BY_ID_QUERY, rota_song_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Rota song not found")

                result = await conn.execute(DELETE_ROTA_SONG_QUERY, rota_song_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Rota song not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting rota_song data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
