from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.plan import PlanService
from fastapi.responses import JSONResponse

class PlanController:
    def __init__(self, plan_service: PlanService):
        self.plan_service = plan_service

    async def fetch_plan_controller(self, filters: dict = {}):
        try:
            plans = await self.plan_service.get_plan_data(filters)
            data = jsonable_encoder(plans)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve plan data",
                "error": str(err)
            })

    async def save_plan_controller(self, request: Request):
        body = await request.json()
        try:
            await self.plan_service.save_plan_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": body
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })
    async def save_bulk_plan_controller(self, request: Request):
        body = await request.json()
        try:
            await self.plan_service.save_bulk_plan_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": body
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })


    async def update_plan_controller(self, request: Request):
        body = await request.json()
        try:
            await self.plan_service.update_plan_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_plan_controller(self, plan_id: str):
        try:
            await self.plan_service.delete_plan_data(plan_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully deleted"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Delete failed",
                "error": str(err)
            })

