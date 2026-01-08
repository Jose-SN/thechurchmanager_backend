from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from datetime import datetime
from app.api import dependencies
from app.queries.account import (
    GET_ACCOUNTS_QUERY,
    GET_ACCOUNT_BY_ID_QUERY,
    GET_ACCOUNTS_BY_ORGANIZATION_QUERY,
    INSERT_ACCOUNT_QUERY,
    UPDATE_ACCOUNT_QUERY,
    DELETE_ACCOUNT_QUERY,
)

class AccountService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse ISO 8601 date string to datetime object"""
        try:
            # Handle ISO format with Z or timezone
            if 'Z' in date_str:
                date_str = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(date_str)
        except (ValueError, AttributeError) as e:
            logging.warning(f"Invalid date format: {date_str}, error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}. Expected ISO 8601 format.")

    def _validate_account_data(self, data: dict, is_update: bool = False) -> dict:
        """Validate account data according to requirements"""
        errors = []
        
        # date: Required, ISO 8601 format
        if not is_update or 'date' in data:
            if 'date' not in data or not data['date']:
                errors.append({"field": "date", "message": "Date is required"})
            else:
                try:
                    self._parse_datetime(data['date'])
                except HTTPException:
                    errors.append({"field": "date", "message": "Date must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)"})
        
        # type: Required, enum: income or expense
        if not is_update or 'type' in data:
            if 'type' not in data or not data['type']:
                errors.append({"field": "type", "message": "Type is required"})
            else:
                type_value = str(data['type']).lower()
                if type_value not in ['income', 'expense']:
                    errors.append({"field": "type", "message": "Type must be either 'income' or 'expense'"})
                else:
                    data['type'] = type_value  # Normalize to lowercase
        
        # payment_type: Optional, enum: VIS, CR, TFR, BP
        if 'payment_type' in data and data['payment_type']:
            payment_type = str(data['payment_type']).upper()
            if payment_type not in ['VIS', 'CR', 'TFR', 'BP']:
                errors.append({"field": "payment_type", "message": "Payment type must be one of: VIS, CR, TFR, BP"})
            else:
                data['payment_type'] = payment_type
        
        # description: Required, 1-500 characters
        if not is_update or 'description' in data:
            if 'description' not in data or not data['description']:
                errors.append({"field": "description", "message": "Description is required"})
            else:
                description = str(data['description']).strip()
                if len(description) < 1:
                    errors.append({"field": "description", "message": "Description cannot be empty"})
                elif len(description) > 500:
                    errors.append({"field": "description", "message": "Description must be 500 characters or less"})
                else:
                    data['description'] = description
        
        # paid_out: Optional, number >= 0, default 0
        if 'paid_out' in data:
            try:
                paid_out = float(data['paid_out']) if data['paid_out'] is not None else 0
                if paid_out < 0:
                    errors.append({"field": "paid_out", "message": "Paid out must be greater than or equal to 0"})
                data['paid_out'] = paid_out
            except (ValueError, TypeError):
                errors.append({"field": "paid_out", "message": "Paid out must be a valid number"})
        elif not is_update:
            data['paid_out'] = 0
        
        # paid_in: Optional, number >= 0, default 0
        if 'paid_in' in data:
            try:
                paid_in = float(data['paid_in']) if data['paid_in'] is not None else 0
                if paid_in < 0:
                    errors.append({"field": "paid_in", "message": "Paid in must be greater than or equal to 0"})
                data['paid_in'] = paid_in
            except (ValueError, TypeError):
                errors.append({"field": "paid_in", "message": "Paid in must be a valid number"})
        elif not is_update:
            data['paid_in'] = 0
        
        # organization_id: Required, valid UUID
        if not is_update or 'organization_id' in data:
            if 'organization_id' not in data or not data['organization_id']:
                errors.append({"field": "organization_id", "message": "Organization ID is required"})
            else:
                try:
                    import uuid
                    uuid.UUID(str(data['organization_id']))
                except (ValueError, AttributeError):
                    errors.append({"field": "organization_id", "message": "Organization ID must be a valid UUID"})
        
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed",
                    "errors": errors
                }
            )
        
        return data

    async def get_account_data(self, filters: dict = {}) -> List[dict]:
        """Get account data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    account = await conn.fetchrow(GET_ACCOUNT_BY_ID_QUERY, filters["id"])
                    if account:
                        return [dependencies.convert_db_types(dict(account))]
                    return []
                elif "organization_id" in filters:
                    rows = await conn.fetch(
                        GET_ACCOUNTS_BY_ORGANIZATION_QUERY,
                        filters["organization_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                rows = await conn.fetch(GET_ACCOUNTS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching account data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_account_data(self, account_data: dict) -> dict:
        """Save new account"""
        try:
            # Validate data
            validated_data = self._validate_account_data(account_data, is_update=False)
            
            async with self.db_pool.acquire() as conn:
                # Parse date
                date = self._parse_datetime(validated_data['date'])
                
                # Extract values
                type_value = validated_data.get('type', '').lower()
                payment_type = validated_data.get('payment_type')
                description = validated_data.get('description', '')
                paid_out = validated_data.get('paid_out', 0)
                paid_in = validated_data.get('paid_in', 0)
                organization_id = validated_data.get('organization_id')
                
                row = await conn.fetchrow(
                    INSERT_ACCOUNT_QUERY,
                    date,
                    type_value,
                    payment_type,
                    description,
                    paid_out,
                    paid_in,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving account data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_account_data(self, account_id: str, account_data: dict) -> dict:
        """Update existing account"""
        if not account_id:
            raise HTTPException(status_code=400, detail="Account ID is required")
        
        try:
            # Validate data
            validated_data = self._validate_account_data(account_data, is_update=True)
            
            async with self.db_pool.acquire() as conn:
                # Check if account exists
                existing = await conn.fetchrow(GET_ACCOUNT_BY_ID_QUERY, account_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Account not found")
                
                # Merge existing data with update data
                merged_data = dict(existing)
                merged_data.update(validated_data)
                
                # Parse date
                date = self._parse_datetime(merged_data['date'])
                
                # Extract values
                type_value = merged_data.get('type', '').lower()
                payment_type = merged_data.get('payment_type')
                description = merged_data.get('description', '')
                paid_out = merged_data.get('paid_out', 0)
                paid_in = merged_data.get('paid_in', 0)
                organization_id = merged_data.get('organization_id')
                
                row = await conn.fetchrow(
                    UPDATE_ACCOUNT_QUERY,
                    date,
                    type_value,
                    payment_type,
                    description,
                    paid_out,
                    paid_in,
                    organization_id,
                    account_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Account not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating account data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_account_data(self, account_id: str) -> str:
        """Delete account"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_ACCOUNT_QUERY, account_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Account not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting account data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

