from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.module import ModuleService
from fastapi.responses import JSONResponse

class ModuleController:
    def __init__(self, module_service: ModuleService):
        self.module_service = module_service

    async def fetch_module_controller(self):
        try:
            modules = await self.module_service.get_module_data()
            data = jsonable_encoder(modules)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve module data",
                "error": str(err)
            })

    async def save_module_controller(self, request: Request):
        body = await request.json()
        try:
            await self.module_service.save_module_data(body)
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
    async def save_bulk_module_controller(self, request: Request):
        body = await request.json()
        try:
            await self.module_service.save_bulk_module_data(body)
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


    async def update_module_controller(self, request: Request):
        body = await request.json()
        try:
            await self.module_service.update_module_data(body)
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

    async def delete_module_controller(self, module_id: str):
        try:
            await self.module_service.delete_module_data(module_id)
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

