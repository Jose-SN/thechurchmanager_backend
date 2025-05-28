from typing import Optional, List, Union
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from your_project.db.models import GuestModel, UserModel  # adapt to your project structure
from your_project.schemas import GuestCreate, GuestUpdate, GuestInDB, UserInDB

class GuestService:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.guest_collection = db_client.your_db.guests
        self.user_collection = db_client.your_db.users

    async def get_guest_data(self, guest_id: Optional[str] = None) -> Union[List[GuestInDB], GuestInDB, None]:
        if guest_id:
            data = await self.guest_collection.find_one({"_id": ObjectId(guest_id)})
            return GuestInDB(**data) if data else None
        else:
            cursor = self.guest_collection.find()
            data = await cursor.to_list(length=100)
            return [GuestInDB(**item) for item in data]

    async def get_guest_users(self, guest_id: Optional[str] = None) -> List[UserInDB]:
        if guest_id:
            cursor = self.user_collection.find({"guestId": ObjectId(guest_id)})
        else:
            cursor = self.user_collection.find()
        data = await cursor.to_list(length=100)
        return [UserInDB(**item) for item in data]

    async def save_guest_data(self, guest: GuestCreate) -> GuestInDB:
        doc = guest.dict(exclude_unset=True)
        result = await self.guest_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return GuestInDB(**doc)

    async def update_guest_data(self, guest: GuestUpdate) -> Optional[GuestInDB]:
        guest_id = guest.id or guest._id
        if not guest_id:
            return await self.save_guest_data(guest)

        update_data = guest.dict(exclude_unset=True, exclude={"id", "_id"})
        updated = await self.guest_collection.find_one_and_update(
            {"_id": ObjectId(guest_id)},
            {"$set": update_data},
            return_document=True
        )
        return GuestInDB(**updated) if updated else None

    async def delete_guest_data(self, guest_id: str) -> str:
        result = await self.guest_collection.find_one_and_delete({"_id": ObjectId(guest_id)})
        return "" if result else "Guest not found"
