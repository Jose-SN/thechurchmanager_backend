from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import PlanController
from app.api.services import PlanService
from app.api.dependencies import get_db

plan_router = APIRouter(tags=["Plan"])

def get_plan_service(db=Depends(get_db)):
    return PlanService(db)

def get_plan_controller(plan_service=Depends(get_plan_service)):
    return PlanController(plan_service)

@plan_router.get("/get")
async def get_all_plans(plan_controller: PlanController = Depends(get_plan_controller),
    _id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if _id:
        filters["_id"] = _id
    if organization_id:
        filters["organization_id"] = organization_id
    return await plan_controller.fetch_plan_controller(filters)

@plan_router.post("/save")
async def save_plan(request: Request, plan_controller: PlanController = Depends(get_plan_controller)):
    return await plan_controller.save_plan_controller(request)

@plan_router.post("/bulk-save")
async def save_bulk_plan(request: Request, plan_controller: PlanController = Depends(get_plan_controller)):
    return await plan_controller.save_bulk_plan_controller(request)

@plan_router.put("/update")
async def update_plan(request: Request, plan_controller: PlanController = Depends(get_plan_controller)):
    return await plan_controller.update_plan_controller(request)

@plan_router.delete("/delete/{plan_id}")
async def delete_plan(plan_id: str, plan_controller: PlanController = Depends(get_plan_controller)):
    return await plan_controller.delete_plan_controller(plan_id)