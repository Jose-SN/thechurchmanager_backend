from typing import List
from fastapi import HTTPException
import asyncpg
import json

from app.queries.role import (
    GET_ROLES_QUERY,
    GET_ROLE_BY_ID_QUERY,
    GET_ROLES_BY_ORGANIZATION_QUERY,
    GET_ROLES_BY_TEAM_QUERY,
    INSERT_ROLE_QUERY,
    INSERT_BULK_ROLES_QUERY,
    UPDATE_ROLE_QUERY,
    DELETE_ROLE_QUERY,
)

class RoleService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_role_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters:
                role_id = filters.get("id")
                role = await conn.fetchrow(GET_ROLE_BY_ID_QUERY, role_id)
                if role:
                    return [dict(role)]
                return []
            elif "organization_id" in filters:
                rows = await conn.fetch(GET_ROLES_BY_ORGANIZATION_QUERY, filters["organization_id"])
                return [dict(row) for row in rows]
            elif "team_id" in filters:
                rows = await conn.fetch(GET_ROLES_BY_TEAM_QUERY, filters["team_id"])
                return [dict(row) for row in rows]
            rows = await conn.fetch(GET_ROLES_QUERY)
            return [dict(row) for row in rows]

    async def save_role_data(self, role_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_ROLE_QUERY
            name = role_data.get("name", "")
            description = role_data.get("description", "")
            team_id = role_data.get("team_id")
            organization_id = role_data.get("organization_id")
            type = role_data.get("type", "")
            # Convert permissions to JSON string for JSONB column
            permissions = role_data.get("permissions", [])
            if isinstance(permissions, (list, dict)):
                permissions = json.dumps(permissions)
            elif permissions is None:
                permissions = json.dumps([])
            
            row = await conn.fetchrow(INSERT_ROLE_QUERY, name, description, team_id, organization_id, type, permissions)
            return dict(row) if row else {}

    async def save_bulk_role_data(self, roles_data: list[dict]) -> list[dict]:
        """
        Bulk insert roles and return the inserted role documents.
        """
        rows = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for role in roles_data:
                    name = role.get("name", "")
                    description = role.get("description", "")
                    team_id = role.get("team_id")
                    organization_id = role.get("organization_id")
                    type = role.get("type", "")
                    # Convert permissions to JSON string for JSONB column
                    permissions = role.get("permissions", [])
                    if isinstance(permissions, (list, dict)):
                        permissions = json.dumps(permissions)
                    elif permissions is None:
                        permissions = json.dumps([])
                    
                    row = await conn.fetchrow(INSERT_ROLE_QUERY, name, description, team_id, organization_id, type, permissions)
                    if row:
                        rows.append(dict(row))
        return rows

    async def update_role_data(self, role_data: dict) -> dict:
        role_id = role_data.get("id")
        if not role_id:
            raise HTTPException(status_code=400, detail="Role ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in role_data.items() if k not in ("id")}
            name = update_data.get("name", "")
            description = update_data.get("description", "")
            team_id = update_data.get("team_id")
            organization_id = update_data.get("organization_id", "")
            type = update_data.get("type", "")
            # Convert permissions to JSON string for JSONB column
            permissions = update_data.get("permissions", [])
            if isinstance(permissions, (list, dict)):
                permissions = json.dumps(permissions)
            elif permissions is None:
                permissions = json.dumps([])
            
            row = await conn.fetchrow(UPDATE_ROLE_QUERY, name, description, team_id, organization_id, type, permissions, role_id)
            if not row:
                raise ValueError("Role not found")
            return dict(row)

    async def delete_role_data(self, role_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_ROLE_QUERY, role_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Role not found"
