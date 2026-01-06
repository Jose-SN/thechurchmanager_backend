from fastapi import APIRouter, Depends, Query, Request, Path
from typing import Optional
from app.api.controllers import TeacherController
from app.api.services import TeacherService
from app.api.dependencies import get_db

teacher_router = APIRouter(tags=["Teacher"])

def get_teacher_service(db=Depends(get_db)):
    return TeacherService(db)

def get_teacher_controller(teacher_service=Depends(get_teacher_service)):
    return TeacherController(teacher_service)

@teacher_router.post("/save", status_code=201)
async def save_teacher(request: Request, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    """Create a new teacher."""
    return await teacher_controller.save_teacher_controller(request)

@teacher_router.post("/bulk-save", status_code=201)
async def save_bulk_teacher(request: Request, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    """Create multiple teachers."""
    return await teacher_controller.save_bulk_teacher_controller(request)

@teacher_router.get("/get")
async def get_teachers(
    teacher_controller: TeacherController = Depends(get_teacher_controller),
    id: Optional[str] = Query(None, description="Teacher ID"),
    organization_id: Optional[str] = Query(None, description="Organization ID")
):
    """Get list of teachers filtered by organization_id."""
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    return await teacher_controller.fetch_teacher_controller(filters)

@teacher_router.get("/get/{teacher_id}")
async def get_teacher_by_id(
    teacher_id: str = Path(..., description="ID of the teacher to retrieve"),
    teacher_controller: TeacherController = Depends(get_teacher_controller)
):
    """Get a single teacher by ID."""
    return await teacher_controller.get_teacher_by_id_controller(teacher_id)

@teacher_router.put("/update/{teacher_id}")
async def update_teacher(
    teacher_id: str = Path(..., description="ID of the teacher to update"),
    request: Request,
    teacher_controller: TeacherController = Depends(get_teacher_controller)
):
    """Update an existing teacher."""
    return await teacher_controller.update_teacher_controller(teacher_id, request)

@teacher_router.delete("/delete/{teacher_id}")
async def delete_teacher(
    teacher_id: str = Path(..., description="ID of the teacher to delete"),
    teacher_controller: TeacherController = Depends(get_teacher_controller)
):
    """Delete a teacher."""
    return await teacher_controller.delete_teacher_controller(teacher_id)
