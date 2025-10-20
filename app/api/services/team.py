from datetime import datetime, timedelta
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

    async def get_team_data(self) -> List[dict]:
        teams = await self.teams.find({}).to_list(length=None)
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
    
    
    async def save_bulk_team_data(self, teams_data: list[dict]) -> list[dict]:
        """
        Bulk insert teams and return the inserted team documents.
        """
        result = await self.teams.insert_many(teams_data)
        inserted_ids = result.inserted_ids
        teams = await self.teams.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return teams


    async def update_team_data(self, team_data: dict) -> dict:
        team_id = team_data.get("id")
        # if not team_id or not ObjectId.is_valid(team_id):
        #     raise ValueError("Invalid team ID")

        # if "password" in team_data and team_data["password"]:
        #     team_data["password"] = pwd_context.hash(team_data["password"])

        update_result = await self.teams.find_one_and_update(
            {"_id": str(team_id)},
            {"$set": team_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Team not found")
        return update_result

    async def delete_team_data(self, team_id: str) -> str:
        if not ObjectId.is_valid(team_id):
            raise HTTPException(status_code=400, detail="Invalid team ID")
        result = await self.teams.find_one_and_delete({"_id": str(team_id)})
        return "" if result else "Team not found"
