from fastapi import Request, HTTPException
from app.api.services.checklist_template import ChecklistTemplateService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime


class ChecklistTemplateController:
    def __init__(self, service: ChecklistTemplateService):
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
            return JSONResponse({"success": True, "data": data, "count": len(data)}, status_code=200)
        except HTTPException as e:
            return JSONResponse({"success": False, "error": {"message": e.detail}}, status_code=e.status_code)
        except Exception as err:
            logging.error(f"fetch checklist template: {err}")
            return JSONResponse({"success": False, "error": {"message": str(err)}}, status_code=500)

    async def get_by_id(self, id: str) -> JSONResponse:
        try:
            rows = await self.service.get_data({"id": id})
            if not rows:
                raise HTTPException(404, "Checklist template not found")
            return JSONResponse({"success": True, "data": self._format(dict(rows[0]))}, status_code=200)
        except HTTPException as e:
            return JSONResponse({"success": False, "error": {"message": e.detail}}, status_code=e.status_code)
        except Exception as err:
            logging.error(f"get checklist template: {err}")
            return JSONResponse({"success": False, "error": {"message": str(err)}}, status_code=500)

    async def save(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as e:
            return JSONResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status_code=400)
        try:
            result = await self.service.save_data(body)
            data = self._format(dict(result))
            if "items" in data and isinstance(data["items"], list):
                data["items"] = [self._format(dict(it)) for it in data["items"]]
            return JSONResponse({"success": True, "message": "Saved", "data": data}, status_code=201)
        except HTTPException as e:
            return JSONResponse({"success": False, "error": {"message": e.detail}}, status_code=e.status_code)
        except Exception as err:
            logging.error(f"save checklist template: {err}")
            return JSONResponse({"success": False, "error": {"message": str(err)}}, status_code=500)

    async def update(self, id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as e:
            return JSONResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status_code=400)
        try:
            result = await self.service.update_data(id, body)
            return JSONResponse({"success": True, "message": "Updated", "data": self._format(dict(result))}, status_code=200)
        except HTTPException as e:
            return JSONResponse({"success": False, "error": {"message": e.detail}}, status_code=e.status_code)
        except Exception as err:
            logging.error(f"update checklist template: {err}")
            return JSONResponse({"success": False, "error": {"message": str(err)}}, status_code=500)

    async def delete(self, id: str) -> JSONResponse:
        try:
            await self.service.delete_data(id)
            return JSONResponse({"success": True, "message": "Deleted"}, status_code=200)
        except HTTPException as e:
            return JSONResponse({"success": False, "error": {"message": e.detail}}, status_code=e.status_code)
        except Exception as err:
            logging.error(f"delete checklist template: {err}")
            return JSONResponse({"success": False, "error": {"message": str(err)}}, status_code=500)
