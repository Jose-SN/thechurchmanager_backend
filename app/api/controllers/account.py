from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.services import AccountService
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

class AccountController:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def _format_response_data(self, data: dict) -> dict:
        """Format response data: convert UUIDs to strings and format timestamps"""
        formatted_data = data.copy()
        
        # Convert UUID objects to strings
        for key, value in formatted_data.items():
            if isinstance(value, uuid.UUID):
                formatted_data[key] = str(value)
        
        # Format timestamps to ISO format
        timestamp_fields = ['date', 'created_at', 'updated_at']
        for field in timestamp_fields:
            if field in formatted_data and formatted_data[field]:
                try:
                    if isinstance(formatted_data[field], datetime):
                        formatted_data[field] = formatted_data[field].isoformat()
                    elif isinstance(formatted_data[field], str):
                        try:
                            dt = datetime.fromisoformat(formatted_data[field].replace('Z', '+00:00'))
                            formatted_data[field] = dt.isoformat()
                        except:
                            pass
                except:
                    pass
        
        return formatted_data

    async def fetch_account_controller(self, filters: dict = {}) -> JSONResponse:
        """Get list of accounts"""
        try:
            accounts = await self.account_service.get_account_data(filters)
            formatted_accounts = [self._format_response_data(dict(account)) for account in accounts]
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_accounts,
                "count": len(formatted_accounts)
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail} if isinstance(e.detail, str) else e.detail
            })
        except Exception as err:
            logging.error(f"Error in fetch_account_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve account data", "details": str(err)}
            })

    async def get_account_by_id_controller(self, account_id: str) -> JSONResponse:
        """Get a single account by ID"""
        try:
            filters = {"id": account_id}
            accounts = await self.account_service.get_account_data(filters)
            if not accounts:
                raise HTTPException(status_code=404, detail="Account not found")
            formatted_account = self._format_response_data(dict(accounts[0]))
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": formatted_account
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail} if isinstance(e.detail, str) else e.detail
            })
        except Exception as err:
            logging.error(f"Error in get_account_by_id_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": {"message": "Failed to retrieve account data", "details": str(err)}
            })

    async def save_account_controller(self, request: Request) -> JSONResponse:
        """Create a new account"""
        body = await request.json()
        try:
            result = await self.account_service.save_account_data(body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=201, content={
                "success": True,
                "message": "Account created successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail} if isinstance(e.detail, str) else e.detail
            })
        except Exception as err:
            logging.error(f"Error in save_account_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Save failed",
                "error": {"message": str(err)}
            })

    async def update_account_controller(self, account_id: str, request: Request) -> JSONResponse:
        """Update an existing account"""
        body = await request.json()
        try:
            result = await self.account_service.update_account_data(account_id, body)
            formatted_result = self._format_response_data(dict(result))
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Account updated successfully",
                "data": formatted_result
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail} if isinstance(e.detail, str) else e.detail
            })
        except Exception as err:
            logging.error(f"Error in update_account_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Update failed",
                "error": {"message": str(err)}
            })

    async def delete_account_controller(self, account_id: str) -> JSONResponse:
        """Delete an account"""
        try:
            await self.account_service.delete_account_data(account_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Account deleted successfully"
            })
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={
                "success": False,
                "error": {"message": e.detail} if isinstance(e.detail, str) else e.detail
            })
        except Exception as err:
            logging.error(f"Error in delete_account_controller: {err}")
            return JSONResponse(status_code=500, content={
                "success": False,
                "message": "Delete failed",
                "error": {"message": str(err)}
            })

