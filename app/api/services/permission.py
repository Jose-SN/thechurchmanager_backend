from typing import List
from fastapi import HTTPException
import asyncpg
import json

from app.queries.permission import (
    GET_PERMISSIONS_QUERY,
    GET_PERMISSION_BY_ID_QUERY,
    GET_PERMISSIONS_BY_ORGANIZATION_QUERY,
    GET_PERMISSIONS_BY_ROLE_QUERY,
    GET_PERMISSIONS_BY_MODULE_QUERY,
    GET_PERMISSIONS_BY_TEAM_QUERY,
    INSERT_PERMISSION_QUERY,
    INSERT_BULK_PERMISSIONS_QUERY,
    UPDATE_PERMISSION_QUERY,
    DELETE_PERMISSION_QUERY,
)

class PermissionService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_permission_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters or "_id" in filters:
                permission_id = filters.get("id") or filters.get("_id")
                permission = await conn.fetchrow(GET_PERMISSION_BY_ID_QUERY, permission_id)
                if permission:
                    return [dict(permission)]
                return []
            elif "organization_id" in filters:
                rows = await conn.fetch(GET_PERMISSIONS_BY_ORGANIZATION_QUERY, filters["organization_id"])
                return [dict(row) for row in rows]
            elif "role_id" in filters:
                rows = await conn.fetch(GET_PERMISSIONS_BY_ROLE_QUERY, filters["role_id"])
                return [dict(row) for row in rows]
            elif "module_id" in filters:
                rows = await conn.fetch(GET_PERMISSIONS_BY_MODULE_QUERY, filters["module_id"])
                return [dict(row) for row in rows]
            elif "team_id" in filters:
                rows = await conn.fetch(GET_PERMISSIONS_BY_TEAM_QUERY, filters["team_id"])
                return [dict(row) for row in rows]
            rows = await conn.fetch(GET_PERMISSIONS_QUERY)
            return [dict(row) for row in rows]

    async def save_permission_data(self, permission_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_PERMISSION_QUERY
            organization_id = permission_data.get("organization_id")
            role_id = permission_data.get("role_id")
            module_id = permission_data.get("module_id")
            team_id = permission_data.get("team_id")
            # Convert permissions object to JSON string for JSONB column
            permissions_obj = permission_data.get("permissions", {})
            if isinstance(permissions_obj, dict):
                permissions = json.dumps(permissions_obj)
            elif permissions_obj is None:
                permissions = json.dumps({})
            else:
                permissions = json.dumps(permissions_obj)
            
            row = await conn.fetchrow(INSERT_PERMISSION_QUERY, organization_id, role_id, module_id, team_id, permissions)
            return dict(row) if row else {}

    async def save_bulk_permission_data(self, permissions_data: list[dict], organization_id: str) -> list[dict]:
        """
        Save or update multiple permissions.
        - Updates permissions that already have id or _id.
        - Creates new permissions that don't.
        Returns the full list of updated/created permission documents.
        """
        updated_permissions = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for permission in permissions_data:
                    permission_id = permission.get("id") or permission.get("_id")
                    
                    if permission_id:
                        # Update existing permission
                        try:
                            update_data = {k: v for k, v in permission.items() if k not in ("_id", "id")}
                            org_id = update_data.get("organization_id", organization_id)
                            role_id = update_data.get("role_id")
                            module_id = update_data.get("module_id")
                            team_id = update_data.get("team_id")
                            # Convert permissions object to JSON string
                            permissions_obj = update_data.get("permissions", {})
                            if isinstance(permissions_obj, dict):
                                permissions = json.dumps(permissions_obj)
                            elif permissions_obj is None:
                                permissions = json.dumps({})
                            else:
                                permissions = json.dumps(permissions_obj)
                            
                            row = await conn.fetchrow(UPDATE_PERMISSION_QUERY, org_id, role_id, module_id, team_id, permissions, permission_id)
                            if row:
                                updated_permissions.append(dict(row))
                            else:
                                # Fallback: if not found, insert as new
                                org_id = permission.get("organization_id", organization_id)
                                role_id = permission.get("role_id")
                                module_id = permission.get("module_id")
                                team_id = permission.get("team_id")
                                permissions_obj = permission.get("permissions", {})
                                if isinstance(permissions_obj, dict):
                                    permissions = json.dumps(permissions_obj)
                                else:
                                    permissions = json.dumps({})
                                
                                row = await conn.fetchrow(INSERT_PERMISSION_QUERY, org_id, role_id, module_id, team_id, permissions)
                                if row:
                                    updated_permissions.append(dict(row))
                        except Exception as e:
                            print(f"⚠️ Error updating permission {permission_id}: {e}")
                            # Fallback: insert as new
                            org_id = permission.get("organization_id", organization_id)
                            role_id = permission.get("role_id")
                            module_id = permission.get("module_id")
                            team_id = permission.get("team_id")
                            permissions_obj = permission.get("permissions", {})
                            if isinstance(permissions_obj, dict):
                                permissions = json.dumps(permissions_obj)
                            else:
                                permissions = json.dumps({})
                            
                            row = await conn.fetchrow(INSERT_PERMISSION_QUERY, org_id, role_id, module_id, team_id, permissions)
                            if row:
                                updated_permissions.append(dict(row))
                    else:
                        # No id → new permission
                        org_id = permission.get("organization_id", organization_id)
                        role_id = permission.get("role_id")
                        module_id = permission.get("module_id")
                        team_id = permission.get("team_id")
                        permissions_obj = permission.get("permissions", {})
                        if isinstance(permissions_obj, dict):
                            permissions = json.dumps(permissions_obj)
                        else:
                            permissions = json.dumps({})
                        
                        row = await conn.fetchrow(INSERT_PERMISSION_QUERY, org_id, role_id, module_id, team_id, permissions)
                        if row:
                            updated_permissions.append(dict(row))
        
        return updated_permissions

    async def update_permission_data(self, permission_data: dict) -> dict:
        permission_id = permission_data.get("id") or permission_data.get("_id")
        if not permission_id:
            raise HTTPException(status_code=400, detail="Permission ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in permission_data.items() if k not in ("_id", "id")}
            organization_id = update_data.get("organization_id", "")
            role_id = update_data.get("role_id")
            module_id = update_data.get("module_id")
            team_id = update_data.get("team_id")
            # Convert permissions object to JSON string
            permissions_obj = update_data.get("permissions", {})
            if isinstance(permissions_obj, dict):
                permissions = json.dumps(permissions_obj)
            elif permissions_obj is None:
                permissions = json.dumps({})
            else:
                permissions = json.dumps(permissions_obj)
            
            row = await conn.fetchrow(UPDATE_PERMISSION_QUERY, organization_id, role_id, module_id, team_id, permissions, permission_id)
            if not row:
                raise ValueError("Permission not found")
            return dict(row)

    async def delete_permission_data(self, permission_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_PERMISSION_QUERY, permission_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Permission not found"
