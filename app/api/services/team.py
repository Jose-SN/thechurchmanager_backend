from datetime import datetime, timedelta
from warnings import filters
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class TeamService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.teams = db["teams"]

    async def get_team_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "_id" in query:
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        teams = await self.teams.find(query).to_list(length=None)
        for team in teams:
            if "_id" in team:
                team["_id"] = str(team["_id"])
        return teams

    async def save_team_data(self, team_data: dict) -> dict:
        # Hash password before save
        # if "password" in team_data and team_data["password"]:
        #     team_data["password"] = pwd_context.hash(team_data["password"])

        result = await self.teams.insert_one(team_data)
        team = await self.teams.find_one({"_id": result.inserted_id})
        return team if team is not None else {}
    
    
        
    async def save_bulk_team_data(self, teams_data: list[dict], organization_id: str) -> list[dict]:
        """
        Save or update multiple teams.
        - Updates teams that already have _id.
        - Creates new teams that don't.
        Returns the full list of updated/created team documents.
        """

        updated_teams = []

        for team in teams_data:
            # ✅ If _id exists, try updating
            if team.get("_id"):
                try:
                    team_id = str(team["_id"])
                    update_data = {k: v for k, v in team.items() if k != "_id"}

                    updated_team = await self.teams.find_one_and_update(
                        {"_id": dependencies.try_objectid(team_id)},
                        {"$set": update_data},
                        return_document=True
                    )

                    if updated_team:
                        updated_teams.append(dependencies.convert_objectid(updated_team))
                    else:
                        # fallback: if not found, insert as new
                        team["organization_id"] = organization_id
                        insert_result = await self.teams.insert_one(team)
                        new_team = await self.teams.find_one({"_id": insert_result.inserted_id})
                        
                        updated_teams.append(dependencies.convert_objectid(new_team))
                except Exception as e:
                    print(f"⚠️ Error updating team {team.get('_id')}: {e}")

            else:
                # ✅ No _id → new team
                team["organization_id"] = organization_id
                insert_result = await self.teams.insert_one(team)
                new_team = await self.teams.find_one({"_id": insert_result.inserted_id})
                updated_teams.append(dependencies.convert_objectid(new_team))

        return updated_teams


    async def update_team_data(self, team_data: dict) -> dict:
        team_id = team_data.get("_id")
        # if not team_id or not ObjectId.is_valid(team_id):
        #     raise ValueError("Invalid team ID")

        # if "password" in team_data and team_data["password"]:
        #     team_data["password"] = pwd_context.hash(team_data["password"])

        update_fields = team_data.copy()
        update_fields.pop("_id", None)

        update_result = await self.teams.find_one_and_update(
            {"_id": dependencies.try_objectid(team_id)},
            {"$set": update_fields},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Team not found")
        return update_result

    async def delete_team_data(self, team_id: str) -> str:
        if not ObjectId.is_valid(team_id):
            raise HTTPException(status_code=400, detail="Invalid team ID")
        result = await self.teams.find_one_and_delete({"_id": ObjectId(team_id)})
        return "" if result else "Team not found"
