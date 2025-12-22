from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.user_role import (
    GET_USER_ROLES_QUERY,
    GET_USER_ROLE_BY_ID_QUERY,
    GET_USER_ROLES_BY_ORGANIZATION_QUERY,
    GET_USER_ROLES_BY_USER_QUERY,
    GET_USER_ROLES_BY_USER_AND_ORGANIZATION_QUERY,
    GET_USER_ROLES_BY_ROLE_QUERY,
    GET_USER_ROLES_BY_TEAM_QUERY,
    INSERT_USER_ROLE_QUERY,
    INSERT_BULK_USER_ROLES_QUERY,
    UPDATE_USER_ROLE_QUERY,
    DELETE_USER_ROLE_QUERY,
    DELETE_USER_ROLE_BY_USER_AND_ROLE_QUERY,
)

class UserRoleService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_user_role_data(self, filters: dict = {}) -> List[dict]:
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters or "_id" in filters:
                    user_role_id = filters.get("id") or filters.get("_id")
                    user_role = await conn.fetchrow(GET_USER_ROLE_BY_ID_QUERY, user_role_id)
                    if user_role:
                        return [dict(user_role)]
                    return []
                elif "user_id" in filters and "organization_id" in filters:
                    # Both user_id and organization_id provided - use combined query
                    rows = await conn.fetch(GET_USER_ROLES_BY_USER_AND_ORGANIZATION_QUERY, filters["user_id"], filters["organization_id"])
                    return [dict(row) for row in rows]
                elif "organization_id" in filters:
                    rows = await conn.fetch(GET_USER_ROLES_BY_ORGANIZATION_QUERY, filters["organization_id"])
                    return [dict(row) for row in rows]
                elif "user_id" in filters:
                    rows = await conn.fetch(GET_USER_ROLES_BY_USER_QUERY, filters["user_id"])
                    return [dict(row) for row in rows]
                elif "role_id" in filters:
                    rows = await conn.fetch(GET_USER_ROLES_BY_ROLE_QUERY, filters["role_id"])
                    return [dict(row) for row in rows]
                elif "team_id" in filters:
                    rows = await conn.fetch(GET_USER_ROLES_BY_TEAM_QUERY, filters["team_id"])
                    return [dict(row) for row in rows]
                rows = await conn.fetch(GET_USER_ROLES_QUERY)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Error fetching user role data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_user_role_data(self, user_role_data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                # Extract values in the correct order for INSERT_USER_ROLE_QUERY
                organization_id = user_role_data.get("organization_id")
                user_id = user_role_data.get("user_id")
                role_id = user_role_data.get("role_id")
                team_id = user_role_data.get("team_id")
                
                row = await conn.fetchrow(INSERT_USER_ROLE_QUERY, organization_id, user_id, role_id, team_id)
                return dict(row) if row else {}
        except Exception as e:
            print(f"❌ Error saving user role data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_bulk_user_role_data(self, user_roles_data: list[dict]) -> list[dict]:
        """
        Bulk insert user roles and return the inserted user role documents.
        """
        try:
            rows = []
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    for user_role in user_roles_data:
                        organization_id = user_role.get("organization_id")
                        user_id = user_role.get("user_id")
                        role_id = user_role.get("role_id")
                        team_id = user_role.get("team_id")
                        
                        row = await conn.fetchrow(INSERT_USER_ROLE_QUERY, organization_id, user_id, role_id, team_id)
                        if row:
                            rows.append(dict(row))
            return rows
        except Exception as e:
            print(f"❌ Error saving bulk user role data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_user_role_data(self, user_role_data: dict) -> dict:
        user_role_id = user_role_data.get("id") or user_role_data.get("_id")
        if not user_role_id:
            raise HTTPException(status_code=400, detail="User Role ID is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                update_data = {k: v for k, v in user_role_data.items() if k not in ("_id", "id")}
                organization_id = update_data.get("organization_id", "")
                user_id = update_data.get("user_id", "")
                role_id = update_data.get("role_id", "")
                team_id = update_data.get("team_id")
                
                row = await conn.fetchrow(UPDATE_USER_ROLE_QUERY, organization_id, user_id, role_id, team_id, user_role_id)
                if not row:
                    raise ValueError("User Role not found")
                return dict(row)
        except ValueError:
            raise
        except Exception as e:
            print(f"❌ Error updating user role data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_user_role_data(self, user_role_id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_USER_ROLE_QUERY, user_role_id)
                if result and result.startswith("DELETE"):
                    return ""
                return "User Role not found"
        except Exception as e:
            print(f"❌ Error deleting user role data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_user_roles_sync(self, user_id: str, organization_id: str, roles_data: list[dict]) -> list[dict]:
        """
        Sync user roles for a specific user within a specific organization.
        - If no existing roles found for this user+organization, create all roles from the request
        - If existing roles found:
          - Delete roles that exist in DB but not in request body
          - Create roles that are in request body but not in DB
          - Keep roles that are in both (no change needed)
        Returns the final list of user roles after sync (filtered by organization).
        """
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # Get all existing user roles for this user
                    existing_rows = await conn.fetch(GET_USER_ROLES_BY_USER_QUERY, user_id)
                    existing_user_roles = [dict(row) for row in existing_rows]
                    
                    # If no existing roles, just create all from request
                    if not existing_user_roles:
                        created_roles = []
                        for role_data in roles_data:
                            role_id = role_data.get("role_id")
                            team_id = role_data.get("team_id")
                            row = await conn.fetchrow(INSERT_USER_ROLE_QUERY, organization_id, user_id, role_id, team_id)
                            if row:
                                created_roles.append(dict(row))
                        return created_roles
                    
                    # Create sets of role_ids for comparison
                    existing_role_ids = {str(ur["role_id"]) for ur in existing_user_roles}
                    requested_role_ids = {str(role.get("role_id")) for role in roles_data if role.get("role_id")}
                    
                    # Delete roles that exist in DB but not in request body
                    roles_to_delete = existing_role_ids - requested_role_ids
                    for role_id_to_delete in roles_to_delete:
                        await conn.execute(DELETE_USER_ROLE_BY_USER_AND_ROLE_QUERY, user_id, role_id_to_delete)
                    
                    # Create roles that are in request body but not in DB
                    roles_to_create = requested_role_ids - existing_role_ids
                    created_roles = []
                    for role_data in roles_data:
                        role_id = role_data.get("role_id")
                        if str(role_id) in roles_to_create:
                            team_id = role_data.get("team_id")
                            row = await conn.fetchrow(INSERT_USER_ROLE_QUERY, organization_id, user_id, role_id, team_id)
                            if row:
                                created_roles.append(dict(row))
                    
                    # Get final list of user roles (existing + newly created)
                    final_rows = await conn.fetch(GET_USER_ROLES_BY_USER_QUERY, user_id)
                    return [dict(row) for row in final_rows]
        except Exception as e:
            print(f"❌ Error syncing user roles: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

