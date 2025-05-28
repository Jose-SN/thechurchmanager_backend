# services/attendance_service.py
from typing import Optional, List
from odmantic import AIOEngine
from db.models import Attendance
from bson import ObjectId

class AttendanceService:
    def __init__(self, engine: AIOEngine):
        self.engine = engine

    async def get_attendance_data(self, attendance_id: Optional[str] = None, submitted_by: Optional[str] = None) -> List[Attendance]:
        if attendance_id:
            attendance = await self.engine.find_one(Attendance, Attendance.id == ObjectId(attendance_id))
            return [attendance] if attendance else []
        elif submitted_by:
            return await self.engine.find(Attendance, Attendance.submittedBy == submitted_by)
        else:
            return await self.engine.find(Attendance)

    async def save_attendance_data(self, attendance_data: Attendance) -> Attendance:
        await self.engine.save(attendance_data)
        return attendance_data

    async def update_attendance_data(self, attendance_id: str, data: dict) -> Optional[Attendance]:
        attendance = await self.engine.find_one(Attendance, Attendance.id == ObjectId(attendance_id))
        if attendance:
            for key, value in data.items():
                setattr(attendance, key, value)
            await self.engine.save(attendance)
            return attendance
        return None

    async def delete_attendance_data(self, attendance_id: str) -> bool:
        attendance = await self.engine.find_one(Attendance, Attendance.id == ObjectId(attendance_id))
        if attendance:
            await self.engine.delete(attendance)
            return True
        return False
