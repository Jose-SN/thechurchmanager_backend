from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from datetime import datetime
from app.api import dependencies
from app.queries.rota import (
    GET_ROTAS_QUERY,
    GET_ROTA_BY_ID_QUERY,
    GET_ROTAS_BY_ORGANIZATION_QUERY,
    GET_ROTAS_BY_TEAM_QUERY,
    SEARCH_ROTAS_QUERY,
    INSERT_ROTA_QUERY,
    UPDATE_ROTA_QUERY,
    DELETE_ROTA_QUERY,
)


class RotaService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _parse_date(self, value) -> datetime | None:
        """Parse date from string or datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return None
        return None

    async def get_rota_data(self, filters: dict = None) -> List[dict]:
        """Get rota data with filtering"""
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    rota = await conn.fetchrow(GET_ROTA_BY_ID_QUERY, filters["id"])
                    if rota:
                        return [dependencies.convert_db_types(dict(rota))]
                    return []
                elif "team_id" in filters:
                    rows = await conn.fetch(
                        GET_ROTAS_BY_TEAM_QUERY,
                        filters["team_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                elif "organization_id" in filters:
                    if any(key in filters for key in ["date", "team_id", "service_type"]):
                        date_val = filters.get("date")
                        if isinstance(date_val, str):
                            date_val = self._parse_date(date_val)
                        rows = await conn.fetch(
                            SEARCH_ROTAS_QUERY,
                            filters["organization_id"],
                            date_val,
                            filters.get("team_id"),
                            filters.get("service_type")
                        )
                    else:
                        rows = await conn.fetch(
                            GET_ROTAS_BY_ORGANIZATION_QUERY,
                            filters["organization_id"]
                        )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]

                rows = await conn.fetch(GET_ROTAS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching rota data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_rota_data(self, rota_data: dict) -> dict:
        """Save new rota"""
        try:
            async with self.db_pool.acquire() as conn:
                date_val = self._parse_date(rota_data.get('date'))
                team_id = rota_data.get('team_id')
                service_type = rota_data.get('service_type')
                notes = rota_data.get('notes')
                organization_id = rota_data.get('organization_id')

                if organization_id is not None:
                    try:
                        organization_id = int(organization_id)
                    except (ValueError, TypeError):
                        organization_id = None

                if date_val is None:
                    raise HTTPException(status_code=400, detail="date is required and must be a valid date")
                if not team_id:
                    raise HTTPException(status_code=400, detail="team_id is required")
                if not organization_id:
                    raise HTTPException(status_code=400, detail="organization_id is required")

                try:
                    team_id = int(team_id)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="team_id must be a valid integer")

                row = await conn.fetchrow(
                    INSERT_ROTA_QUERY,
                    date_val,
                    team_id,
                    service_type,
                    notes,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving rota data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_rota_data(self, rota_id: int, rota_data: dict, organization_id: int) -> dict:
        """Update existing rota"""
        if rota_id is None:
            raise HTTPException(status_code=400, detail="Rota ID is required")
        if organization_id is None:
            raise HTTPException(status_code=400, detail="organization_id is required")

        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_ROTA_BY_ID_QUERY, rota_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Rota not found")

                if int(existing['organization_id']) != int(organization_id):
                    raise HTTPException(status_code=403, detail="Not authorized to update this rota")

                merged_data = dict(existing)
                merged_data.update(rota_data)

                date_val = self._parse_date(merged_data.get('date'))
                team_id = merged_data.get('team_id')
                service_type = merged_data.get('service_type')
                notes = merged_data.get('notes')

                if date_val is None:
                    raise HTTPException(status_code=400, detail="date is required and must be a valid date")
                if not team_id:
                    raise HTTPException(status_code=400, detail="team_id is required")

                try:
                    team_id = int(team_id)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="team_id must be a valid integer")

                row = await conn.fetchrow(
                    UPDATE_ROTA_QUERY,
                    date_val,
                    team_id,
                    service_type,
                    notes,
                    rota_id,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Rota not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating rota data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_rota_data(self, rota_id: int, organization_id: int) -> str:
        """Delete rota"""
        if organization_id is None:
            raise HTTPException(status_code=400, detail="organization_id is required")

        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_ROTA_BY_ID_QUERY, rota_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Rota not found")

                if int(existing['organization_id']) != int(organization_id):
                    raise HTTPException(status_code=403, detail="Not authorized to delete this rota")

                result = await conn.execute(DELETE_ROTA_QUERY, rota_id, organization_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Rota not found or not authorized")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting rota data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
