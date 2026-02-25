from fastapi import Request, HTTPException
from app.api.services.rota_song import RotaSongService
from fastapi.responses import JSONResponse
import logging
from datetime import datetime


class RotaSongController:
    def __init__(self, rota_song_service: RotaSongService):
        self.rota_song_service = rota_song_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data for JSON serialization"""
        formatted = data.copy()
        for key, value in formatted.items():
            if isinstance(value, datetime):
                formatted[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):
                formatted[key] = value.isoformat()
        return formatted

    async def fetch_rota_song_controller(self, filters: dict = None) -> JSONResponse:
        """Get list of rota_songs"""
        try:
            rows = await self.rota_song_service.get_rota_song_data(filters)
            formatted = [self._format_response_data(dict(r)) for r in rows]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted,
                "count": len(formatted)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in fetch_rota_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve rota song data", "details": str(err)}
            })

    async def get_rota_song_by_id_controller(self, rota_song_id: int) -> JSONResponse:
        """Get a single rota_song by ID"""
        try:
            filters = {"id": rota_song_id}
            rows = await self.rota_song_service.get_rota_song_data(filters)
            if not rows:
                raise HTTPException(status_code=404, detail="Rota song not found")
            formatted = self._format_response_data(dict(rows[0]))
            return JSONResponse(status_code=200, content={"success": True, "data": formatted})
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in get_rota_song_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve rota song data", "details": str(err)}
            })

    async def save_rota_song_controller(self, request: Request) -> JSONResponse:
        """Add song to rota"""
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        try:
            result = await self.rota_song_service.save_rota_song_data(body)
            formatted = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Song added to rota successfully",
                "data": formatted
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in save_rota_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_rota_song_controller(self, rota_song_id: int, request: Request) -> JSONResponse:
        """Update rota_song record"""
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        try:
            result = await self.rota_song_service.update_rota_song_data(rota_song_id, body)
            formatted = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Rota song updated successfully",
                "data": formatted
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in update_rota_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_rota_song_controller(self, rota_song_id: int) -> JSONResponse:
        """Remove song from rota"""
        try:
            await self.rota_song_service.delete_rota_song_data(rota_song_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Song removed from rota successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in delete_rota_song_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })
