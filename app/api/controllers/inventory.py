from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.inventory import InventoryService
from fastapi.responses import JSONResponse

class InventoryController:
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    async def fetch_inventory_controller(self, filters: dict = {}):
        try:
            inventorys = await self.inventory_service.get_inventory_data(filters)
            data = jsonable_encoder(inventorys)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve inventory data",
                "error": str(err)
            })

    async def save_inventory_controller(self, request: Request):
        body = await request.json()
        try:
            await self.inventory_service.save_inventory_data(body)
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
    async def save_bulk_inventory_controller(self, request: Request):
        body = await request.json()
        try:
            await self.inventory_service.save_bulk_inventory_data(body)
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


    async def update_inventory_controller(self, request: Request):
        body = await request.json()
        try:
            await self.inventory_service.update_inventory_data(body)
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

    async def delete_inventory_controller(self, inventory_id: str):
        try:
            await self.inventory_service.delete_inventory_data(inventory_id)
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

