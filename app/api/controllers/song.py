from fastapi import Request, HTTPException
from app.api.services.song import SongService
from fastapi.responses import JSONResponse
import logging
from datetime import datetime


class SongController:
    def __init__(self, song_service: SongService):
        self.song_service = song_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data for JSON serialization"""
        formatted_data = data.copy()

        for key, value in formatted_data.items():
            if isinstance(value, datetime):
                formatted_data[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):
                formatted_data[key] = value.isoformat()

        return formatted_data

    async def fetch_song_controller(self, filters: dict = None) -> JSONResponse:
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

    async def get_song_by_id_controller(self, song_id: int) -> JSONResponse:
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

    async def update_song_controller(self, song_id: int, request: Request) -> JSONResponse:
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
            if organization_id is None:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })

            try:
                org_id = int(organization_id)
            except (ValueError, TypeError):
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id must be a valid integer"}
                })

            result = await self.song_service.update_song_data(song_id, body, org_id)
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

    async def delete_song_controller(self, song_id: int, organization_id: int) -> JSONResponse:
        """Delete a song"""
        try:
            if organization_id is None:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })

            try:
                org_id = int(organization_id)
            except (ValueError, TypeError):
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id must be a valid integer"}
                })

            await self.song_service.delete_song_data(song_id, org_id)
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
