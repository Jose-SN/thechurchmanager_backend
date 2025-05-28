from fastapi import HTTPException
from typing import List, Optional
from guest_service import GuestService
from guest_schemas import GuestCreate, GuestUpdate, GuestDB

guest_service = GuestService()

class GuestController:

    async def fetch_guest(self, guest_id: Optional[str] = None) -> List[GuestDB]:
        guests = await guest_service.get_guest(guest_id)
        if guest_id and not guests:
            raise HTTPException(status_code=404, detail="Guest not found")
        return guests

    async def insert_guest(self, guest_data: GuestCreate) -> GuestDB:
        guest = await guest_service.save_guest(guest_data)
        return guest

    async def update_guest(self, guest_data: GuestUpdate) -> GuestDB:
        updated_guest = await guest_service.update_guest(guest_data)
        if not updated_guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        return updated_guest

    async def remove_guest(self, guest_id: str):
        deleted = await guest_service.delete_guest(guest_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Guest not found")
        return {"success": True, "message": "Successfully deleted"}

guest_controller = GuestController()
