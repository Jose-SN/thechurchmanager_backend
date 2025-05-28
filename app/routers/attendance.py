from fastapi import APIRouter
from .event import AttendanceController
from .schemas import AttendanceSchema

router = APIRouter()
controller = AttendanceController()

@router.get("/get")
def get_attendance(attendance_id: str = None, submitted_by: str = None):
    return controller.get_attendance(attendance_id, submitted_by)

@router.post("/save")
def save_attendance(data: AttendanceSchema):
    return controller.save_attendance(data)

@router.put("/update/{attendance_id}")
def update_attendance(attendance_id: str, data: AttendanceSchema):
    return controller.update_attendance(attendance_id, data)

@router.delete("/delete/{attendance_id}")
def delete_attendance(attendance_id: str):
    return controller.delete_attendance(attendance_id)
