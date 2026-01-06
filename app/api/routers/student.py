from fastapi import APIRouter, Depends, Query, Request, Path
from typing import Optional
from app.api.controllers import StudentController
from app.api.services import StudentService
from app.api.dependencies import get_db

student_router = APIRouter(tags=["Student"])

def get_student_service(db=Depends(get_db)):
    return StudentService(db)

def get_student_controller(student_service=Depends(get_student_service)):
    return StudentController(student_service)

@student_router.post("/save", status_code=201)
async def save_student(request: Request, student_controller: StudentController = Depends(get_student_controller)):
    """Create a new student."""
    return await student_controller.save_student_controller(request)

@student_router.get("/get")
async def get_students(
    student_controller: StudentController = Depends(get_student_controller),
    id: Optional[str] = Query(None, description="Student ID"),
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    class_id: Optional[str] = Query(None, description="Class ID")
):
    """Get list of students filtered by organization_id or class_id."""
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    if class_id:
        filters["class_id"] = class_id
    return await student_controller.fetch_student_controller(filters)

@student_router.get("/get/{student_id}")
async def get_student_by_id(
    student_id: str = Path(..., description="ID of the student to retrieve"),
    student_controller: StudentController = Depends(get_student_controller)
):
    """Get a single student by ID."""
    return await student_controller.get_student_by_id_controller(student_id)

@student_router.put("/update/{student_id}")
async def update_student(
    student_id: str = Path(..., description="ID of the student to update"),
    request: Request,
    student_controller: StudentController = Depends(get_student_controller)
):
    """Update an existing student."""
    return await student_controller.update_student_controller(student_id, request)

@student_router.delete("/delete/{student_id}")
async def delete_student(
    student_id: str = Path(..., description="ID of the student to delete"),
    student_controller: StudentController = Depends(get_student_controller)
):
    """Delete a student."""
    return await student_controller.delete_student_controller(student_id)

