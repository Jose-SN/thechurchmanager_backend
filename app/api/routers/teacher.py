from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, TeacherController
from app.api.services import UserService, TeacherService
from app.api.dependencies import get_db

teacher_router = APIRouter(tags=["Teacher"])

def get_teacher_service(db=Depends(get_db)):
    return TeacherService(db)

def get_teacher_controller(teacher_service=Depends(get_teacher_service)):
    return TeacherController(teacher_service)

@teacher_router.get("/get")
async def get_all_teachers(teacher_controller: TeacherController = Depends(get_teacher_controller),
    _id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if _id:
        filters["_id"] = _id
    if organization_id:
        filters["organization_id"] = organization_id
    return await teacher_controller.fetch_teacher_controller(filters)

@teacher_router.post("/save")
async def save_teacher(request: Request, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    return await teacher_controller.save_teacher_controller(request)

@teacher_router.post("/bulk-save")
async def save_bulk_teacher(request: Request, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    return await teacher_controller.save_bulk_teacher_controller(request)

@teacher_router.put("/update")
async def update_teacher(request: Request, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    return await teacher_controller.update_teacher_controller(request)

@teacher_router.delete("/delete/{teacher_id}")
async def delete_teacher(teacher_id: str, teacher_controller: TeacherController = Depends(get_teacher_controller)):
    return await teacher_controller.delete_teacher_controller(teacher_id)