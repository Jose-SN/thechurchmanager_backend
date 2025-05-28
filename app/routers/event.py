from fastapi import APIRouter, Query, Path
from .event import EventController
from .schemas import EventSchema

router = APIRouter()
controller = EventController()

@router.get("/get")
async def get_event(eventId: str = Query(default=None), submittedBy: str = Query(default=None)):
    return await controller.fetch_event(eventId, submittedBy)

@router.post("/save")
async def save_event(event_data: EventSchema):
    return await controller.insert_event(event_data)

@router.post("/end-event/{eventId}")
async def end_event(eventId: str = Path(...), end_time: str = Query(default=None)):
    return await controller.end_event(eventId, end_time)

@router.put("/update")
async def update_event(event_data: EventSchema):
    return await controller.update_event(event_data)

@router.delete("/delete/{eventId}")
async def delete_event(eventId: str = Path(...)):
    return await controller.remove_event(eventId)
