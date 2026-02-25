from fastapi import Request, HTTPException
from app.api.services.rota import RotaService
from fastapi.responses import JSONResponse
import logging
from datetime import datetime


class RotaController:
    def __init__(self, rota_service: RotaService):
        self.rota_service = rota_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data for JSON serialization"""
        formatted_data = data.copy()

        for key, value in formatted_data.items():
            if isinstance(value, datetime):
                formatted_data[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):
                formatted_data[key] = value.isoformat()

        return formatted_data

    async def fetch_rota_controller(self, filters: dict = None) -> JSONResponse:
        """Get list of rotas"""
        try:
            rotas = await self.rota_service.get_rota_data(filters)
            formatted_rotas = [self._format_response_data(dict(rota)) for rota in rotas]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_rotas,
                "count": len(formatted_rotas)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in fetch_rota_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve rota data", "details": str(err)}
            })

    async def get_rota_by_id_controller(self, rota_id: int) -> JSONResponse:
        """Get a single rota by ID"""
        try:
            filters = {"id": rota_id}
            rotas = await self.rota_service.get_rota_data(filters)
            if not rotas:
                raise HTTPException(status_code=404, detail="Rota not found")
            formatted_rota = self._format_response_data(dict(rotas[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_rota
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in get_rota_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve rota data", "details": str(err)}
            })

    async def save_rota_controller(self, request: Request) -> JSONResponse:
        """Create a new rota"""
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })

        try:
            result = await self.rota_service.save_rota_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Rota saved successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_rota_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_rota_controller(self, rota_id: int, request: Request) -> JSONResponse:
        """Update an existing rota"""
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

            result = await self.rota_service.update_rota_data(rota_id, body, org_id)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Rota updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in update_rota_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_rota_controller(self, rota_id: int, organization_id: int) -> JSONResponse:
        """Delete a rota"""
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

            await self.rota_service.delete_rota_data(rota_id, org_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Rota deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in delete_rota_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })
