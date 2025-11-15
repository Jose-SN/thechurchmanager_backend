from typing import Optional, List, Union
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.api import dependencies
# from schemas import MeetingCreate, MeetingUpdate, MeetingInDB

class MeetingService:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.collection = db_client.your_db.meetings  # adjust db/collection names

    async def get_meeting_data(self, meeting_id: Optional[str] = None, submitted_by: Optional[str] = None) ->   Union[dict, List[dict], None]:
        if meeting_id:
            data = await self.collection.find_one({"_id": ObjectId(meeting_id)})
            return data if data else None
        elif submitted_by:
            cursor = self.collection.find({"submittedBy": ObjectId(submitted_by)})
            data = await cursor.to_list(length=100)  # limit as needed
            return [item for item in data]
        else:
            cursor = self.collection.find()
            data = await cursor.to_list(length=100)
            return [item for item in data]

    async def save_meeting_data(self, meeting) -> dict:
        doc = meeting.dict(exclude_unset=True)
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def update_meeting_data(self, meeting) -> Optional[dict]:
        meeting_id = meeting.id or meeting._id
        if not meeting_id:
            # If no id, treat as new document
            return await self.save_meeting_data(meeting)

        update_data = meeting.dict(exclude_unset=True, exclude={"id", "_id"})
        updated = await self.collection.find_one_and_update(
            {"_id": dependencies.try_objectid(meeting_id)},
            {"$set": update_data},
            return_document=True
        )
        return updated if updated else None

    async def delete_meeting_data(self, meeting_id: str) -> str:
        result = await self.collection.find_one_and_delete({"_id": dependencies.try_objectid(meeting_id)})
        return "" if result else "Meeting not found"
