from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services.inventory import InventoryService
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import uuid
from datetime import datetime, date

class InventoryController:
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data: convert UUIDs to strings and format dates"""
        formatted_data = data.copy()
        
        # Convert UUID objects to strings
        for key, value in formatted_data.items():
            if isinstance(value, uuid.UUID):
                formatted_data[key] = str(value)
        
        # Format dates to ISO format
        date_fields = ['purchase_date', 'patch_test_date', 'warranty_date']
        timestamp_fields = ['created_at', 'updated_at']
        
        for field in date_fields:
            if field in formatted_data and formatted_data[field]:
                # Format as YYYY-MM-DD
                try:
                    if isinstance(formatted_data[field], (datetime, date)):
                        formatted_data[field] = formatted_data[field].strftime('%Y-%m-%d')
                    elif isinstance(formatted_data[field], str):
                        # Try to parse and reformat if needed
                        try:
                            dt = datetime.fromisoformat(formatted_data[field].replace('Z', '+00:00'))
                            formatted_data[field] = dt.strftime('%Y-%m-%d')
                        except:
                            # If parsing fails, keep original string
                            pass
                except:
                    pass
        
        for field in timestamp_fields:
            if field in formatted_data and formatted_data[field]:
                # Format as ISO timestamp
                try:
                    if isinstance(formatted_data[field], datetime):
                        formatted_data[field] = formatted_data[field].isoformat()
                    elif isinstance(formatted_data[field], str):
                        # Try to parse and reformat if needed
                        try:
                            dt = datetime.fromisoformat(formatted_data[field].replace('Z', '+00:00'))
                            formatted_data[field] = dt.isoformat()
                        except:
                            # Keep original string
                            pass
                except:
                    pass
        
        return formatted_data

    async def fetch_inventory_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of inventories"""
        try:
            inventories = await self.inventory_service.get_inventory_data(filters)
            
            # Convert to camelCase and format
            formatted_data = [self._format_response_data(dict(inv)) for inv in inventories]
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": formatted_data,
                    "count": len(formatted_data)
                }
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.detail
                }
            )
        except Exception as err:
            logging.error(f"Error fetching inventory: {err}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to retrieve inventory data",
                    "error": str(err)
                }
            )

    async def get_inventory_by_id_controller(self, inventory_id: str) -> JSONResponse:
        """Get single inventory item by ID"""
        try:
            inventories = await self.inventory_service.get_inventory_data({"id": inventory_id})
            
            if not inventories:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": "Inventory not found"
                    }
                )
            
            formatted_data = self._format_response_data(dict(inventories[0]))
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": formatted_data
                }
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.detail
                }
            )
        except Exception as err:
            logging.error(f"Error fetching inventory by ID: {err}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to retrieve inventory data",
                    "error": str(err)
                }
            )

    async def save_inventory_controller(self, request: Request) -> JSONResponse:
        """Create a new inventory item"""
        try:
            body = await request.json()
            result = await self.inventory_service.save_inventory_data(body)
            
            if not result:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": "Failed to save inventory"
                    }
                )
            
            formatted_data = self._format_response_data(result)
            
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "Inventory saved successfully",
                    "data": formatted_data
                }
            )
        except HTTPException as e:
            error_detail = e.detail
            if isinstance(error_detail, dict) and "errors" in error_detail:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": error_detail
                    }
                )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {"message": str(error_detail)}
                }
            )
        except Exception as err:
            logging.error(f"Error saving inventory: {err}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Save failed",
                    "error": str(err)
                }
            )

    async def update_inventory_controller(self, inventory_id: str, request: Request) -> JSONResponse:
        """Update an existing inventory item"""
        try:
            body = await request.json()
            result = await self.inventory_service.update_inventory_data(inventory_id, body)
            
            formatted_data = self._format_response_data(result)
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Inventory updated successfully",
                    "data": formatted_data
                }
            )
        except HTTPException as e:
            error_detail = e.detail
            if isinstance(error_detail, dict) and "errors" in error_detail:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": error_detail
                    }
                )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {"message": str(error_detail)}
                }
            )
        except Exception as err:
            logging.error(f"Error updating inventory: {err}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Update failed",
                    "error": str(err)
                }
            )

    async def delete_inventory_controller(self, inventory_id: str) -> JSONResponse:
        """Delete an inventory item"""
        try:
            await self.inventory_service.delete_inventory_data(inventory_id)
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Inventory deleted successfully"
                }
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {"message": str(e.detail)}
                }
            )
        except Exception as err:
            logging.error(f"Error deleting inventory: {err}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Delete failed",
                    "error": str(err)
                }
            )
