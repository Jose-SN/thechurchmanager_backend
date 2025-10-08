from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Optional
from pydantic import BaseModel
from utils import get_current_user  # your auth dependency
from schemas import MeetingCreate, MeetingUpdate  # your pydantic schemas
from controllers import (
    fetch_meeting,
    insert_meeting,
    update_meeting,
    remove_meeting
)

router = APIRouter(prefix="/meeting", tags=["Meeting"])

@router.get("/get")
async def get_meetings(current_user=Depends(get_current_user)):
    return await fetch_meeting()

@router.post("/save", status_code=status.HTTP_201_CREATED)
async def create_meeting(meeting: MeetingCreate, current_user=Depends(get_current_user)):
    return await insert_meeting(meeting)

@router.put("/update")
async def put_meeting(meeting: MeetingUpdate, current_user=Depends(get_current_user)):
    return await update_meeting(meeting)

@router.delete("/delete/{meetingid}")
async def delete_meeting(meetingid: str = Path(...), current_user=Depends(get_current_user)):
    return await remove_meeting(meetingid)
