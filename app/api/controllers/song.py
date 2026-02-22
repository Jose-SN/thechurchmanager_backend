from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services.song import SongService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

class SongController:
    def __init__(self, song_service: SongService):
        self.song_service = song_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data: convert UUIDs to strings and format timestamps"""
        formatted_data = data.copy()
        
        # Convert UUID objects to strings
        for key, value in formatted_data.items():
            if isinstance(value, uuid.UUID):
                formatted_data[key] = str(value)
        
        # Format timestamps to ISO format
        timestamp_fields = ['created_at', 'updated_at']
        for field in timestamp_fields:
            if field in formatted_data and formatted_data[field]:
                try:
                    if isinstance(formatted_data[field], datetime):
                        formatted_data[field] = formatted_data[field].isoformat()
                    elif isinstance(formatted_data[field], str):
                        try:
                            dt = datetime.fromisoformat(formatted_data[field].replace('Z', '+00:00'))
                            formatted_data[field] = dt.isoformat()
                        except:
                            pass
                except:
                    pass
        
        return formatted_data

    async def fetch_song_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of songs"""
        try:
            songs = await self.song_service.get_song_data(filters)
            formatted_songs = [self._format_response_data(dict(song)) for song in songs]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_songs,
                "count": len(formatted_songs)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in fetch_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve song data", "details": str(err)}
            })

    async def get_song_by_id_controller(self, song_id: str) -> JSONResponse:
        """Get a single song by ID"""
        try:
            filters = {"id": song_id}
            songs = await self.song_service.get_song_data(filters)
            if not songs:
                raise HTTPException(status_code=404, detail="Song not found")
            formatted_song = self._format_response_data(dict(songs[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_song
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in get_song_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve song data", "details": str(err)}
            })

    async def save_song_controller(self, request: Request) -> JSONResponse:
        """Create a new song"""
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        
        try:
            result = await self.song_service.save_song_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Song saved successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_song_controller(self, song_id: str, request: Request) -> JSONResponse:
        """Update an existing song"""
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        
        try:
            organization_id = body.pop('organization_id', None)
            if not organization_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })
            
            result = await self.song_service.update_song_data(song_id, body, organization_id)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Song updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in update_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_song_controller(self, song_id: str, organization_id: str) -> JSONResponse:
        """Delete a song"""
        try:
            if not organization_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })
            
            await self.song_service.delete_song_data(song_id, organization_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Song deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in delete_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })
