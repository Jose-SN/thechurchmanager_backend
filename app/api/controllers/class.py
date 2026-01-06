from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services.class import ClassService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

class ClassController:
    def __init__(self, class_service: ClassService):
        self.class_service = class_service

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

    async def fetch_class_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of classes"""
        try:
            classes = await self.class_service.get_class_data(filters)
            formatted_classes = [self._format_response_data(dict(class_item)) for class_item in classes]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_classes,
                "count": len(formatted_classes)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in fetch_class_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve class data", "details": str(err)}
            })

    async def get_class_by_id_controller(self, class_id: str) -> JSONResponse:
        """Get a single class by ID"""
        try:
            filters = {"id": class_id}
            classes = await self.class_service.get_class_data(filters)
            if not classes:
                raise HTTPException(status_code=404, detail="Class not found")
            formatted_class = self._format_response_data(dict(classes[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_class
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in get_class_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve class data", "details": str(err)}
            })

    async def save_class_controller(self, request: Request) -> JSONResponse:
        """Create a new class"""
        body = await request.json()
        try:
            result = await self.class_service.save_class_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Class saved successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_class_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_class_controller(self, class_id: str, request: Request) -> JSONResponse:
        """Update an existing class"""
        body = await request.json()
        try:
            result = await self.class_service.update_class_data(class_id, body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Class updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in update_class_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_class_controller(self, class_id: str) -> JSONResponse:
        """Delete a class"""
        try:
            await self.class_service.delete_class_data(class_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Class deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in delete_class_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })

