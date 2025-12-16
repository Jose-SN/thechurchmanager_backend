from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.team import (
    GET_TEAMS_QUERY,
    GET_TEAM_BY_ID_QUERY,
    GET_TEAMS_BY_ORGANIZATION_QUERY,
    INSERT_TEAM_QUERY,
    INSERT_BULK_TEAMS_QUERY,
    UPDATE_TEAM_QUERY,
    DELETE_TEAM_QUERY,
)

class TeamService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_team_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters:
                team_id = filters.get("id")
                team = await conn.fetchrow(GET_TEAM_BY_ID_QUERY, team_id)
                if team:
                    return [dict(team)]
                return []
            elif "organization_id" in filters:
                rows = await conn.fetch(GET_TEAMS_BY_ORGANIZATION_QUERY, filters["organization_id"])
                return [dict(row) for row in rows]
            rows = await conn.fetch(GET_TEAMS_QUERY)
            return [dict(row) for row in rows]

    async def save_team_data(self, team_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_TEAM_QUERY
            name = team_data.get("name", "")
            organization_id = team_data.get("organization_id")
            description = team_data.get("description", "")
            row = await conn.fetchrow(INSERT_TEAM_QUERY, name, description, organization_id)
            return dict(row) if row else {}

    async def save_bulk_team_data(self, teams_data: list[dict], organization_id: str) -> list[dict]:
        """
        Save or update multiple teams.
        - Updates teams that already have id.
        - Creates new teams that don't.
        Returns the full list of updated/created team documents.
        """
        updated_teams = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for team in teams_data:
                    team_id = team.get("id")
                    
                    if team_id:
                        # Update existing team
                        try:
                            update_data = {k: v for k, v in team.items() if k not in ("id")}
                            name = update_data.get("name", "")
                            description = update_data.get("description", "")
                            org_id = update_data.get("organization_id", organization_id)
                            
                            row = await conn.fetchrow(UPDATE_TEAM_QUERY, name, description, org_id, team_id)
                            if row:
                                updated_teams.append(dict(row))
                            else:
                                # Fallback: if not found, insert as new
                                name = team.get("name", "")
                                description = team.get("description", "")
                                row = await conn.fetchrow(INSERT_TEAM_QUERY, name, description, organization_id)
                                if row:
                                    updated_teams.append(dict(row))
                        except Exception as e:
                            print(f"⚠️ Error updating team {team_id}: {e}")
                            # Fallback: insert as new
                            name = team.get("name", "")
                            description = team.get("description", "")
                            row = await conn.fetchrow(INSERT_TEAM_QUERY, name, description, organization_id)
                            if row:
                                updated_teams.append(dict(row))
                    else:
                        # No id → new team
                        name = team.get("name", "")
                        description = team.get("description", "")
                        row = await conn.fetchrow(INSERT_TEAM_QUERY, name, description, organization_id)
                        if row:
                            updated_teams.append(dict(row))
        
        return updated_teams

    async def update_team_data(self, team_data: dict) -> dict:
        team_id = team_data.get("id")
        if not team_id:
            raise HTTPException(status_code=400, detail="Team ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in team_data.items() if k not in ("id")}
            name = update_data.get("name", "")
            description = update_data.get("description", "")
            organization_id = update_data.get("organization_id", "")
            
            row = await conn.fetchrow(UPDATE_TEAM_QUERY, name, description, organization_id, team_id)
            if not row:
                raise ValueError("Team not found")
            return dict(row)

    async def delete_team_data(self, team_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_TEAM_QUERY, team_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Team not found"
