# services/status_service.py
from typing import Optional, List, Union
from models.status import Status
from schemas.status import StatusCreate, StatusUpdate
from bson import ObjectId

class StatusService:

    async def get_status_data(self, status_id: Optional[str] = None, created_by: Optional[str] = None) -> Union[Status, List[Status], None]:
        if status_id:
            status = await Status.get(ObjectId(status_id))
            return status
        elif created_by:
            statuses = await Status.find(Status.createdBy == created_by).to_list()
            return statuses
        else:
            statuses = await Status.find_all().to_list()
            return statuses

    async def get_status_overview(self):
        # Beanie does not support complex MongoDB aggregations directly,
        # so we use the underlying motor collection:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "parentId": "$parentId",
                        "parentType": "$parentType"
                    },
                    "statuses": {
                        "$push": {
                            "_id": "$_id",
                            "percentage": "$percentage",
                            "comment": "$comment",
                            "rating": "$rating",
                            "reward": "$reward",
                            "createdBy": "$createdBy",
                            "creation_date": "$creation_date",
                            "modification_date": "$modification_date"
                        }
                    },
                    "averageRating": {"$avg": "$rating"},
                    "maxPercentage": {"$max": "$percentage"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "parentId": "$_id.parentId",
                    "parentType": "$_id.parentType",
                    "statuses": 1,
                    "averageRating": 1,
                    "maxPercentage": 1
                }
            }
        ]

        result = await Status.get_motor_collection().aggregate(pipeline).to_list(length=None)
        return result

    async def save_status_data(self, status_create: StatusCreate) -> Status:
        new_status = Status(**status_create.dict())
        await new_status.insert()
        return new_status

    async def update_status_data(self, status_update: StatusUpdate) -> Optional[Status]:
        if status_update.id is None:
            # Insert new if no id provided
            new_status = Status(**status_update.dict(exclude={"id"}, exclude_none=True))
            await new_status.insert()
            return new_status

        existing_status = await Status.get(status_update.id)
        if existing_status is None:
            return None

        update_data = status_update.dict(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(existing_status, key, value)
        await existing_status.save()
        return existing_status

    async def delete_status_data(self, status_id: str) -> str:
        status = await Status.get(ObjectId(status_id))
        if status:
            await status.delete()
            return ""
        return "Status not found"
