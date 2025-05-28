from fastapi import HTTPException
from .service import AttendanceService
from .schemas import AttendanceSchema

service = AttendanceService()

class AttendanceController:
    def get_attendance(self, attendance_id=None, submitted_by=None):
        result = service.get_attendance(attendance_id, submitted_by)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Attendance not found")

    def save_attendance(self, data: AttendanceSchema):
        saved = service.save_attendance(data.dict())
        return {
            "success": True,
            "message": "Successfully added",
            "data": saved.to_json()
        }

    def update_attendance(self, attendance_id: str, data: AttendanceSchema):
        updated = service.update_attendance(attendance_id, data.dict())
        if updated:
            return {
                "success": True,
                "message": "Successfully updated",
                "data": updated.to_json()
            }
        else:
            raise HTTPException(status_code=404, detail="Attendance not found")

    def delete_attendance(self, attendance_id: str):
        success = service.delete_attendance(attendance_id)
        if success:
            return {
                "success": True,
                "message": "Successfully deleted"
            }
        else:
            raise HTTPException(status_code=404, detail="Attendance not found")
