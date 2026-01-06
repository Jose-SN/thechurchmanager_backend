from typing import List, Optional
from fastapi import HTTPException
import asyncpg
from datetime import datetime
import logging
import uuid
from decimal import Decimal

from app.queries.inventory import (
    GET_INVENTORIES_QUERY,
    GET_INVENTORY_BY_ID_QUERY,
    GET_INVENTORIES_BY_ORGANIZATION_QUERY,
    GET_INVENTORIES_BY_ORGANIZATION_AND_TEAM_QUERY,
    INSERT_INVENTORY_QUERY,
    UPDATE_INVENTORY_QUERY,
    DELETE_INVENTORY_QUERY,
)

class InventoryService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            # Try ISO format first (YYYY-MM-DD or full ISO timestamp)
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, AttributeError) as e:
            logging.warning(f"Invalid date format: {date_str}, error: {e}")
            return None

    def _format_date(self, date_obj) -> Optional[str]:
        """Format datetime/date object to ISO date string (YYYY-MM-DD)"""
        if not date_obj:
            return None
        if isinstance(date_obj, datetime):
            return date_obj.strftime('%Y-%m-%d')
        if isinstance(date_obj, str):
            # If it's already a string, return as is (should be YYYY-MM-DD)
            return date_obj
        # Handle date objects from PostgreSQL
        try:
            return date_obj.strftime('%Y-%m-%d')
        except:
            return str(date_obj)

    def _validate_inventory_data(self, data: dict, is_update: bool = False) -> dict:
        """Validate inventory data according to requirements"""
        errors = []
        
        # item_name: Required, string, 1-255 characters
        if not is_update or 'item_name' in data:
            item_name = data.get('item_name', '').strip() if isinstance(data.get('item_name'), str) else ''
            if not item_name:
                errors.append({"field": "item_name", "message": "Item name is required"})
            elif len(item_name) > 255:
                errors.append({"field": "item_name", "message": "Item name must be 255 characters or less"})
        
        # price: Optional, number, >= 0, max 2 decimal places
        if 'price' in data and data['price'] is not None:
            try:
                # Convert string to float if needed
                price = float(data['price']) if isinstance(data['price'], str) else float(data['price'])
                if price < 0:
                    errors.append({"field": "price", "message": "Price must be greater than or equal to 0"})
            except (ValueError, TypeError):
                errors.append({"field": "price", "message": "Price must be a valid number"})
        
        # stock_left: Required, integer, >= 0
        if not is_update or 'stock_left' in data:
            stock_left = data.get('stock_left')
            if stock_left is None:
                errors.append({"field": "stock_left", "message": "Stock left is required"})
            else:
                try:
                    # Convert string to int if needed
                    stock_left = int(stock_left) if isinstance(stock_left, str) else int(stock_left)
                    if stock_left < 0:
                        errors.append({"field": "stock_left", "message": "Stock left must be greater than or equal to 0"})
                except (ValueError, TypeError):
                    errors.append({"field": "stock_left", "message": "Stock left must be a valid integer"})
        
        # organization_id: Required, valid UUID
        if not is_update or 'organization_id' in data:
            org_id = data.get('organization_id')
            if not org_id:
                errors.append({"field": "organization_id", "message": "Organization ID is required"})
            else:
                try:
                    uuid.UUID(str(org_id))
                except (ValueError, AttributeError):
                    errors.append({"field": "organization_id", "message": "Organization ID must be a valid UUID"})
        
        # team_id: Required, valid UUID
        if not is_update or 'team_id' in data:
            team_id = data.get('team_id')
            if not team_id:
                errors.append({"field": "team_id", "message": "Team ID is required"})
            else:
                try:
                    uuid.UUID(str(team_id))
                except (ValueError, AttributeError):
                    errors.append({"field": "team_id", "message": "Team ID must be a valid UUID"})
        
        # Date validations
        date_fields = ['purchase_date', 'patch_test_date', 'warranty_date']
        for field in date_fields:
            if field in data and data[field] is not None:
                parsed_date = self._parse_date(data[field])
                if parsed_date is None and data[field]:
                    errors.append({"field": field, "message": f"{field} must be a valid date (YYYY-MM-DD or ISO format)"})
        
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed",
                    "errors": errors
                }
            )
        
        return data

    def _convert_db_types(self, row_dict: dict) -> dict:
        """Convert database types (UUID, Decimal) to JSON-serializable types"""
        converted = {}
        for key, value in row_dict.items():
            if isinstance(value, uuid.UUID):
                converted[key] = str(value)
            elif isinstance(value, Decimal):
                converted[key] = float(value)
            else:
                converted[key] = value
        return converted

    async def get_inventory_data(self, filters: dict = {}) -> List[dict]:
        """Get inventory data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    inventory_id = filters.get("id")
                    inventory = await conn.fetchrow(GET_INVENTORY_BY_ID_QUERY, inventory_id)
                    if inventory:
                        return [self._convert_db_types(dict(inventory))]
                    return []
                elif "organization_id" in filters and "team_id" in filters:
                    rows = await conn.fetch(
                        GET_INVENTORIES_BY_ORGANIZATION_AND_TEAM_QUERY,
                        filters["organization_id"],
                        filters["team_id"]
                    )
                    return [self._convert_db_types(dict(row)) for row in rows]
                elif "organization_id" in filters:
                    rows = await conn.fetch(
                        GET_INVENTORIES_BY_ORGANIZATION_QUERY,
                        filters["organization_id"]
                    )
                    return [self._convert_db_types(dict(row)) for row in rows]
                rows = await conn.fetch(GET_INVENTORIES_QUERY)
                return [self._convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching inventory data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    def _convert_types(self, validated_data: dict) -> dict:
        """Convert string values to appropriate types"""
        converted = validated_data.copy()
        
        # Convert price to float/Decimal if it's a string
        if 'price' in converted and converted['price'] is not None:
            try:
                converted['price'] = float(converted['price'])
            except (ValueError, TypeError):
                converted['price'] = None
        
        # Convert stock_left to int if it's a string
        if 'stock_left' in converted and converted['stock_left'] is not None:
            try:
                converted['stock_left'] = int(converted['stock_left'])
            except (ValueError, TypeError):
                converted['stock_left'] = 0
        
        return converted

    async def save_inventory_data(self, inventory_data: dict) -> dict:
        """Save new inventory item"""
        try:
            # Validate data (expects snake_case)
            validated_data = self._validate_inventory_data(inventory_data, is_update=False)
            
            # Convert string types to proper types
            validated_data = self._convert_types(validated_data)
            
            async with self.db_pool.acquire() as conn:
                # Parse dates
                purchase_date = self._parse_date(validated_data.get('purchase_date'))
                patch_test_date = self._parse_date(validated_data.get('patch_test_date'))
                warranty_date = self._parse_date(validated_data.get('warranty_date'))
                
                # Extract values (already converted to proper types)
                item_name = validated_data.get('item_name', '')
                price = validated_data.get('price')
                stock_left = validated_data.get('stock_left', 0)
                organization_id = validated_data.get('organization_id')
                team_id = validated_data.get('team_id')
                
                row = await conn.fetchrow(
                    INSERT_INVENTORY_QUERY,
                    item_name,
                    price,
                    stock_left,
                    purchase_date,
                    patch_test_date,
                    warranty_date,
                    organization_id,
                    team_id
                )
                if row:
                    return self._convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving inventory data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_inventory_data(self, inventory_id: str, inventory_data: dict) -> dict:
        """Update existing inventory item"""
        if not inventory_id:
            raise HTTPException(status_code=400, detail="Inventory ID is required")
        
        try:
            # Validate data (expects snake_case)
            validated_data = self._validate_inventory_data(inventory_data, is_update=True)
            
            # Convert string types to proper types
            validated_data = self._convert_types(validated_data)
            
            # Get existing data first
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_INVENTORY_BY_ID_QUERY, inventory_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Inventory not found")
                
                existing_dict = dict(existing)
                # Merge with new data
                for key, value in validated_data.items():
                    if value is not None:
                        existing_dict[key] = value
                
                # Parse dates
                purchase_date = self._parse_date(existing_dict.get('purchase_date'))
                patch_test_date = self._parse_date(existing_dict.get('patch_test_date'))
                warranty_date = self._parse_date(existing_dict.get('warranty_date'))
                
                # Extract values (ensure proper types)
                item_name = existing_dict.get('item_name', '')
                price = existing_dict.get('price')
                # Ensure stock_left is int
                stock_left = existing_dict.get('stock_left', 0)
                if isinstance(stock_left, str):
                    try:
                        stock_left = int(stock_left)
                    except (ValueError, TypeError):
                        stock_left = 0
                organization_id = existing_dict.get('organization_id')
                team_id = existing_dict.get('team_id')
                
                row = await conn.fetchrow(
                    UPDATE_INVENTORY_QUERY,
                    item_name,
                    price,
                    stock_left,
                    purchase_date,
                    patch_test_date,
                    warranty_date,
                    organization_id,
                    team_id,
                    inventory_id
                )
                if not row:
                    raise HTTPException(status_code=404, detail="Inventory not found")
                return self._convert_db_types(dict(row))
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating inventory data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_inventory_data(self, inventory_id: str) -> str:
        """Delete inventory item"""
        try:
            async with self.db_pool.acquire() as conn:
                # Check if exists first
                existing = await conn.fetchrow(GET_INVENTORY_BY_ID_QUERY, inventory_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Inventory not found")
                
                result = await conn.execute(DELETE_INVENTORY_QUERY, inventory_id)
                if result and result.startswith("DELETE"):
                    return ""
                return "Inventory not found"
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting inventory data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
