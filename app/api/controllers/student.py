from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services.student import StudentService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

class StudentController:
    def __init__(self, student_service: StudentService):
        self.student_service = student_service

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

    async def fetch_student_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of students"""
        try:
            students = await self.student_service.get_student_data(filters)
            formatted_students = [self._format_response_data(dict(student)) for student in students]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_students,
                "count": len(formatted_students)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in fetch_student_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve student data", "details": str(err)}
            })

    async def get_student_by_id_controller(self, student_id: str) -> JSONResponse:
        """Get a single student by ID"""
        try:
            filters = {"id": student_id}
            students = await self.student_service.get_student_data(filters)
            if not students:
                raise HTTPException(status_code=404, detail="Student not found")
            formatted_student = self._format_response_data(dict(students[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_student
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in get_student_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve student data", "details": str(err)}
            })

    async def save_student_controller(self, request: Request) -> JSONResponse:
        """Create a new student"""
        body = await request.json()
        try:
            result = await self.student_service.save_student_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Student saved successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in save_student_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_student_controller(self, student_id: str, request: Request) -> JSONResponse:
        """Update an existing student"""
        body = await request.json()
        try:
            result = await self.student_service.update_student_data(student_id, body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Student updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in update_student_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_student_controller(self, student_id: str) -> JSONResponse:
        """Delete a student"""
        try:
            await self.student_service.delete_student_data(student_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Student deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail}
            })
        except Exception as err:
            logging.error(f"Error in delete_student_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })

