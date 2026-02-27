from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from datetime import datetime, date
from decimal import Decimal
from app.api import dependencies
from app.queries.expense import (
    GET_EXPENSES_QUERY,
    GET_EXPENSE_BY_ID_QUERY,
    GET_EXPENSES_BY_ORGANIZATION_QUERY,
    GET_EXPENSES_BY_TEAM_QUERY,
    SEARCH_EXPENSES_QUERY,
    INSERT_EXPENSE_QUERY,
    UPDATE_EXPENSE_QUERY,
    DELETE_EXPENSE_QUERY,
)


class ExpenseService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _parse_date(self, value) -> date | None:
        if value is None:
            return None
        if isinstance(value, date):
            return value if not isinstance(value, datetime) else value.date()
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.date()
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return None
        return None

    def _parse_decimal(self, value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    async def get_expense_data(self, filters: dict = None) -> List[dict]:
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_EXPENSE_BY_ID_QUERY, filters["id"])
                    if row:
                        return [dependencies.convert_db_types(dict(row))]
                    return []
                elif "team_id" in filters:
                    rows = await conn.fetch(GET_EXPENSES_BY_TEAM_QUERY, filters["team_id"])
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                elif "organization_id" in filters:
                    if any(k in filters for k in ["expense_date", "team_id", "category", "title"]):
                        exp_date = self._parse_date(filters.get("expense_date")) or filters.get("expense_date")
                        rows = await conn.fetch(
                            SEARCH_EXPENSES_QUERY,
                            filters["organization_id"],
                            exp_date,
                            filters.get("team_id"),
                            filters.get("category"),
                            filters.get("title")
                        )
                    else:
                        rows = await conn.fetch(
                            GET_EXPENSES_BY_ORGANIZATION_QUERY,
                            filters["organization_id"]
                        )
                    return [dependencies.convert_db_types(dict(r)) for r in rows]

                rows = await conn.fetch(GET_EXPENSES_QUERY)
                return [dependencies.convert_db_types(dict(r)) for r in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching expense data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_expense_data(self, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                title = (data.get('title') or '').strip()
                amount = self._parse_decimal(data.get('amount'))
                category = data.get('category')
                expense_date = self._parse_date(data.get('expense_date') or data.get('date'))
                description = data.get('description')
                organization_id = data.get('organization_id')
                team_id = data.get('team_id')

                if not organization_id:
                    raise HTTPException(status_code=400, detail="organization_id is required")
                if not title:
                    raise HTTPException(status_code=400, detail="title is required and cannot be empty")
                if amount is None or amount < 0:
                    raise HTTPException(status_code=400, detail="amount is required and must be >= 0")
                if expense_date is None:
                    raise HTTPException(status_code=400, detail="expense_date is required and must be a valid date")

                row = await conn.fetchrow(
                    INSERT_EXPENSE_QUERY,
                    title,
                    amount,
                    category,
                    expense_date,
                    description,
                    organization_id,
                    team_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving expense data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_bulk_expense_data(self, expenses: list) -> dict:
        """Save multiple expenses. Returns success/failure counts and details."""
        results = {"success": True, "total": len(expenses), "successful": 0, "failed": 0, "data": []}
        for item in expenses:
            try:
                row = await self.save_expense_data(item)
                if row:
                    results["successful"] += 1
                    results["data"].append({"status": "success", "data": row})
                else:
                    results["failed"] += 1
                    results["data"].append({"status": "failed", "error": "No data returned"})
            except HTTPException as e:
                results["failed"] += 1
                results["data"].append({"status": "failed", "error": e.detail})
                results["success"] = False
            except Exception as e:
                results["failed"] += 1
                results["data"].append({"status": "failed", "error": str(e)})
                results["success"] = False
        return results

    async def update_expense_data(self, expense_id: int, data: dict, organization_id) -> dict:
        if expense_id is None:
            raise HTTPException(status_code=400, detail="Expense ID is required")
        if not organization_id:
            raise HTTPException(status_code=400, detail="organization_id is required")

        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_EXPENSE_BY_ID_QUERY, expense_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Expense not found")
                if str(existing['organization_id']) != str(organization_id):
                    raise HTTPException(status_code=403, detail="Not authorized to update this expense")

                merged = dict(existing)
                merged.update(data)

                title = (merged.get('title') or '').strip()
                amount = self._parse_decimal(merged.get('amount'))
                category = merged.get('category')
                expense_date = self._parse_date(merged.get('expense_date') or merged.get('date'))
                description = merged.get('description')
                team_id = merged.get('team_id')

                if not title:
                    raise HTTPException(status_code=400, detail="title is required and cannot be empty")
                if amount is None or amount < 0:
                    raise HTTPException(status_code=400, detail="amount must be >= 0")
                if expense_date is None:
                    raise HTTPException(status_code=400, detail="expense_date must be a valid date")

                row = await conn.fetchrow(
                    UPDATE_EXPENSE_QUERY,
                    title,
                    amount,
                    category,
                    expense_date,
                    description,
                    team_id,
                    expense_id,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Expense not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating expense data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_expense_data(self, expense_id: int, organization_id) -> str:
        if not organization_id:
            raise HTTPException(status_code=400, detail="organization_id is required")

        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_EXPENSE_BY_ID_QUERY, expense_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Expense not found")
                if str(existing['organization_id']) != str(organization_id):
                    raise HTTPException(status_code=403, detail="Not authorized to delete this expense")

                result = await conn.execute(DELETE_EXPENSE_QUERY, expense_id, organization_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Expense not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting expense data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
