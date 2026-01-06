from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services.teacher import TeacherService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

class TeacherController:
    def __init__(self, teacher_service: TeacherService):
        self.teacher_service = teacher_service

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

    async def fetch_teacher_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of teachers"""
        try:
            teachers = await self.teacher_service.get_teacher_data(filters)
            formatted_teachers = [self._format_response_data(dict(teacher)) for teacher in teachers]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_teachers,
                "count": len(formatted_teachers)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in fetch_teacher_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve teacher data", "details": str(err)}
            })

    async def get_teacher_by_id_controller(self, teacher_id: str) -> JSONResponse:
        """Get a single teacher by ID"""
        try:
            filters = {"id": teacher_id}
            teachers = await self.teacher_service.get_teacher_data(filters)
            if not teachers:
                raise HTTPException(status_code=404, detail="Teacher not found")
            formatted_teacher = self._format_response_data(dict(teachers[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_teacher
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in get_teacher_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve teacher data", "details": str(err)}
            })

    async def save_teacher_controller(self, request: Request) -> JSONResponse:
        """Create a new teacher"""
        body = await request.json()
        try:
            result = await self.teacher_service.save_teacher_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Teacher saved successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_teacher_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def save_bulk_teacher_controller(self, request: Request) -> JSONResponse:
        """Create multiple teachers"""
        body = await request.json()
        try:
            if not isinstance(body, list):
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "Request body must be an array"}
                })
            result = await self.teacher_service.save_bulk_teacher_data(body)
            formatted_result = [self._format_response_data(dict(teacher)) for teacher in result]
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Teachers saved successfully",
                "data": formatted_result,
                "count": len(formatted_result)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_bulk_teacher_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_teacher_controller(self, teacher_id: str, request: Request) -> JSONResponse:
        """Update an existing teacher"""
        body = await request.json()
        try:
            result = await self.teacher_service.update_teacher_data(teacher_id, body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Teacher updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in update_teacher_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_teacher_controller(self, teacher_id: str) -> JSONResponse:
        """Delete a teacher"""
        try:
            await self.teacher_service.delete_teacher_data(teacher_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Teacher deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in delete_teacher_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })
