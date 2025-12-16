from models import EventModel, CheckoutModel
from schemas import EventSchema
from bson import ObjectId
from datetime import datetime

class EventService:
    async def get_event_data(self, event_id: str = None, submitted_by: str = None):
        if event_id:
            event = await EventModel.find_one({"id": ObjectId(event_id)})
            return event
        elif submitted_by:
            events = await EventModel.find_many({"submittedBy": ObjectId(submitted_by)})
            return events
        else:
            events = await EventModel.find_all()
            return events

    async def save_event_data(self, event: EventSchema):
        event_dict = event.dict(exclude_unset=True)
        event_dict['submittedBy'] = ObjectId(event_dict['submittedBy'])
        inserted_id = await EventModel.insert_one(event_dict)
        return {"id": str(inserted_id)}

    async def end_event_data(self, event_id: str, end: str = None):
        event = await EventModel.find_one({"id": ObjectId(event_id)})
        if not event:
            raise ValueError("Event not found")

        if event.get('ended'):
            raise ValueError("Event already ended")

        end_time = end or datetime.utcnow().isoformat()
        await EventModel.update_one({"id": ObjectId(event_id)}, {"$set": {"ended": True, "end": end_time}})

        current_time = datetime.utcnow().isoformat()
        updated_checkouts = await CheckoutModel.update_many(
            {"eventId": event_id},
            {"$set": {"checkOut": current_time}}
        )

        return {
            "message": "Event ended successfully",
            "updated_checkouts": updated_checkouts
        }

    async def update_event_data(self, event: EventSchema):
        event_dict = event.dict(exclude_unset=True)
        event_id = event_dict.pop('id', None)
        if not event_id:
            raise ValueError("Event ID is required")

        await EventModel.update_one({"id": ObjectId(event_id)}, {"$set": event_dict})
        return {"id": event_id}

    async def delete_event_data(self, event_id: str):
        deleted = await EventModel.delete_one({"id": ObjectId(event_id)})
        if deleted.deleted_count == 0:
            raise ValueError("Event not found")
        return ""
