from fastapi import HTTPException
from schemas import MeetingBase
from services import MeetingService

class MeetingController:
    def __init__(self):
        self.service = MeetingService()

    async def fetch_meeting(self, meeting_id: str = None, submitted_by: str = None):
        try:
            data = await self.service.get_meeting_data(meeting_id, submitted_by)
            return data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve meeting overview data: {str(e)}")

    async def insert_meeting(self, meeting: MeetingBase):
        try:
            result = await self.service.save_meeting_data(meeting)
            return {
                "success": True,
                "message": "Successfully added",
                "data": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

    async def update_meeting(self, meeting_id: str, meeting: MeetingBase):
        try:
            updated = await self.service.update_meeting_data(meeting_id, meeting)
            if not updated:
                raise HTTPException(status_code=404, detail="Meeting not found")
            return {
                "success": True,
                "message": "Successfully updated"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    async def remove_meeting(self, meeting_id: str):
        try:
            result = await self.service.delete_meeting_data(meeting_id)
            if not result:
                raise HTTPException(status_code=404, detail="Meeting not found")
            return {
                "success": True,
                "message": "Successfully deleted"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")
