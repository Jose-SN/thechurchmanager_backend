from fastapi import Request, HTTPException
from app.api.services.expense import ExpenseService
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from decimal import Decimal


class ExpenseController:
    def __init__(self, expense_service: ExpenseService):
        self.expense_service = expense_service

    def _format_response_data(self, data: dict) -> dict:
        formatted = data.copy()
        for key, value in formatted.items():
            if isinstance(value, datetime):
                formatted[key] = value.isoformat()
            elif isinstance(value, Decimal):
                formatted[key] = float(value)
            elif hasattr(value, 'isoformat'):
                formatted[key] = value.isoformat()
        return formatted

    async def fetch_expense_controller(self, filters: dict = None) -> JSONResponse:
        try:
            rows = await self.expense_service.get_expense_data(filters)
            formatted = [self._format_response_data(dict(r)) for r in rows]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted,
                "count": len(formatted)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in fetch_expense_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve expense data", "details": str(err)}
            })

    async def get_expense_by_id_controller(self, expense_id: int) -> JSONResponse:
        try:
            filters = {"id": expense_id}
            rows = await self.expense_service.get_expense_data(filters)
            if not rows:
                raise HTTPException(status_code=404, detail="Expense not found")
            formatted = self._format_response_data(dict(rows[0]))
            return JSONResponse(status_code=200, content={"success": True, "data": formatted})
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in get_expense_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve expense data", "details": str(err)}
            })

    async def save_expense_controller(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        try:
            result = await self.expense_service.save_expense_data(body)
            formatted = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Expense saved successfully",
                "data": formatted
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in save_expense_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def save_bulk_expense_controller(self, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        try:
            expenses = body if isinstance(body, list) else body.get("expenses", [])
            if not expenses:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "expenses array is required and cannot be empty"}
                })
            result = await self.expense_service.save_bulk_expense_data(expenses)
            for item in result.get("data", []):
                if "data" in item and item["data"]:
                    item["data"] = self._format_response_data(dict(item["data"]))
            return JSONResponse(status_code=201, content={
                "success": result.get("success", True),
                "message": f"Bulk save complete: {result.get('successful', 0)} succeeded, {result.get('failed', 0)} failed",
                **result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in save_bulk_expense_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Bulk save failed",
                "error": {"message": str(err)}
            })

    async def update_expense_controller(self, expense_id: int, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except ValueError as json_err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Invalid JSON in request body",
                "error": str(json_err)
            })
        try:
            organization_id = body.pop('organization_id', None)
            if not organization_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })

            result = await self.expense_service.update_expense_data(
                expense_id, body, organization_id
            )
            formatted = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Expense updated successfully",
                "data": formatted
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in update_expense_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_expense_controller(self, expense_id: int, organization_id: str) -> JSONResponse:
        try:
            if not organization_id:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "error": {"message": "organization_id is required"}
                })
            await self.expense_service.delete_expense_data(expense_id, organization_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Expense deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": {"message": e.detail}})
        except Exception as err:
            logging.error(f"Error in delete_expense_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })
