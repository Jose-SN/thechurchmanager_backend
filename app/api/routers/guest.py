from fastapi import APIRouter, Depends
from typing import List, Optional
from schemas import GuestCreate, GuestUpdate, GuestDB
from controllers import guest_controller

router = APIRouter(prefix="/guest", tags=["Guest"])

@router.get("/get", response_model=List[GuestDB])
async def get_all_guests():
    return await guest_controller.fetch_guest()

@router.get("/get/{guest_id}", response_model=GuestDB)
async def get_guest(guest_id: str):
    return await guest_controller.fetch_guest(guest_id)

@router.post("/save", response_model=GuestDB)
async def save_guest(guest: GuestCreate):
    return await guest_controller.insert_guest(guest)

@router.put("/update", response_model=GuestDB)
async def update_guest(guest: GuestUpdate):
    return await guest_controller.update_guest(guest)

@router.delete("/delete/{guest_id}")
async def delete_guest(guest_id: str):
    return await guest_controller.remove_guest(guest_id)
