from fastapi import APIRouter, Depends, Request, Query
from app.api.controllers.user import UserController
from app.api.services.user import UserService
from app.api.dependencies import get_db

user_router = APIRouter(tags=["User"])

def get_user_service(db=Depends(get_db)):
    return UserService(db)

def get_user_controller(user_service=Depends(get_user_service)):
    return UserController(user_service)

@user_router.get("/get")
async def get_all_users(
    user_controller: UserController = Depends(get_user_controller),
    _id: str = Query(None),
    organization_id: str = Query(None)
):
    filters = {}
    if _id:
        filters["_id"] = _id
    if organization_id:
        filters["organization_id"] = organization_id
    return await user_controller.fetch_user_controller(filters)

@user_router.post("/save")
async def save_user(request: Request, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.save_user_controller(request)

@user_router.post("/login")
async def login_user(request: Request, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.login_user_controller(request)


@user_router.post("/bulk-save")
async def save_bulk_user(request: Request, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.save_bulk_user_controller(request)

@user_router.put("/update")
async def update_user(request: Request, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.update_user_controller(request)

@user_router.post("/delete/{user_id}")
async def delete_user(user_id: str, user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.delete_user_controller(user_id)

# from fastapi import APIRouter, Depends, Path, Request
# from app.controller.user import UserController
# from app.service.user import UserService
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.routers import get_db



# # Dependency to get UserService
# def get_user_service(db=Depends(get_db)):
#     return UserService(db)




# # Dependency to get UserController
# def get_user_controller(user_service=Depends(get_user_service)):
#     return UserController(user_service)




# user_router = APIRouter(prefix="/user", tags=["User"])




# @user_router.get("/get")
# async def get_all_users(user_controller: UserController = Depends(get_user_controller)):
#     return await user_controller.fetch_user_controller()
