from fastapi import Request, HTTPException
from app.api.services.checklist_item import ChecklistItemService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime


class ChecklistItemController:
    def __init__(self, service: ChecklistItemService):
        self.service = service

    def _format(self, d: dict) -> dict:
        out = d.copy()
        for k, v in out.items():
            if isinstance(v, uuid.UUID):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            elif hasattr(v, "isoformat"):
                out[k] = v.isoformat()
        return out

    async def fetch(self, filters: dict = None) -> JSONResponse:
        try:
            rows = await self.service.get_data(filters)
            data = [self._format(dict(r)) for r in rows]
            return JSONResponse(200, {"success": True, "data": data, "count": len(data)})
        except HTTPException as e:
            return JSONResponse(e.status_code, {"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"fetch checklist item: {err}")
            return JSONResponse(500, {"success": False, "error": {"message": str(err)}})

    async def get_by_id(self, id: str) -> JSONResponse:
        try:
            rows = await self.service.get_data({"id": id})
            if not rows:
                raise HTTPException(404, "Checklist item not found")
            return JSONResponse(200, {"success": True, "data": self._format(dict(rows[0]))})
        except HTTPException as e:
            return JSONResponse(e.status_code, {"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"get checklist item: {err}")
            return JSONResponse(500, {"success": False, "error": {"message": str(err)}})

    async def save(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as e:
            return JSONResponse(400, {"success": False, "message": "Invalid JSON", "error": str(e)})
        try:
            result = await self.service.save_data(body)
            return JSONResponse(201, {"success": True, "message": "Saved", "data": self._format(dict(result))})
        except HTTPException as e:
            return JSONResponse(e.status_code, {"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"save checklist item: {err}")
            return JSONResponse(500, {"success": False, "error": {"message": str(err)}})

    async def update(self, id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as e:
            return JSONResponse(400, {"success": False, "message": "Invalid JSON", "error": str(e)})
        try:
            result = await self.service.update_data(id, body)
            return JSONResponse(200, {"success": True, "message": "Updated", "data": self._format(dict(result))})
        except HTTPException as e:
            return JSONResponse(e.status_code, {"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"update checklist item: {err}")
            return JSONResponse(500, {"success": False, "error": {"message": str(err)}})

    async def delete(self, id: str) -> JSONResponse:
        try:
            await self.service.delete_data(id)
            return JSONResponse(200, {"success": True, "message": "Deleted"})
        except HTTPException as e:
            return JSONResponse(e.status_code, {"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"delete checklist item: {err}")
            return JSONResponse(500, {"success": False, "error": {"message": str(err)}})
