from fastapi import APIRouter, Depends, Request
from app.api.controllers import UserController, TeamController
from app.api.services import UserService, TeamService
from app.api.dependencies import get_db

team_router = APIRouter(tags=["Team"])

def get_team_service(db=Depends(get_db)):
    return TeamService(db)

def get_team_controller(team_service=Depends(get_team_service)):
    return TeamController(team_service)

@team_router.get("/get")
async def get_all_teams(team_controller: TeamController = Depends(get_team_controller)):
    return await team_controller.fetch_team_controller()

@team_router.post("/save")
async def save_team(request: Request, team_controller: TeamController = Depends(get_team_controller)):
    return await team_controller.save_team_controller(request)

@team_router.post("/bulk-save")
async def save_bulk_team(request: Request, team_controller: TeamController = Depends(get_team_controller)):
    return await team_controller.save_bulk_team_controller(request)

@team_router.put("/update")
async def update_team(request: Request, team_controller: TeamController = Depends(get_team_controller)):
    return await team_controller.update_team_controller(request)

@team_router.post("/delete/{team_id}")
async def delete_team(team_id: str, team_controller: TeamController = Depends(get_team_controller)):
    return await team_controller.delete_team_controller(team_id)