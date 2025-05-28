from fastapi import HTTPException
from service import EventService
from schemas import EventSchema

service = EventService()

class EventController:
    async def fetch_event(self, event_id: str = None, submitted_by: str = None):
        try:
            data = await service.get_event_data(event_id, submitted_by)
            return data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve event data: {str(e)}")

    async def insert_event(self, event_data: EventSchema):
        try:
            saved_event = await service.save_event_data(event_data)
            return {
                "success": True,
                "message": "Successfully added",
                "data": saved_event
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

    async def end_event(self, event_id: str, end_time: str = None):
        try:
            result = await service.end_event_data(event_id, end_time)
            return {
                "success": True,
                "message": "Successfully ended",
                "data": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"End event failed: {str(e)}")

    async def update_event(self, event_data: EventSchema):
        try:
            updated_event = await service.update_event_data(event_data)
            return {
                "success": True,
                "message": "Successfully updated",
                "data": updated_event
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    async def remove_event(self, event_id: str):
        try:
            result = await service.delete_event_data(event_id)
            return {
                "success": True,
                "message": "Successfully deleted" if not result else result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")
