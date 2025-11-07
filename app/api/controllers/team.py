from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.team import TeamService
from fastapi.responses import JSONResponse

class TeamController:
    def __init__(self, team_service: TeamService):
        self.team_service = team_service

    async def fetch_team_controller(self, filters: dict = {}):
        try:
            teams = await self.team_service.get_team_data(filters)
            data = jsonable_encoder(teams)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve team data",
                "error": str(err)
            })

    async def save_team_controller(self, request: Request):
        body = await request.json()
        try:
            await self.team_service.save_team_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": body
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def save_bulk_team_controller(self, request: Request):
        body = await request.json()
        try:
            organization_id = body.get("organization_id")
            teams = body.get("teams", [])
            updated_teams = await self.team_service.save_bulk_team_data(teams, organization_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": updated_teams
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def update_team_controller(self, request: Request):
        body = await request.json()
        try:
            updated_team = await self.team_service.update_team_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated",
                "data": updated_team
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_team_controller(self, team_id: str):
        try:
            await self.team_service.delete_team_data(team_id)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully deleted"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Delete failed",
                "error": str(err)
            })

