from fastapi import APIRouter, Depends
from app.api.controllers.user import UserController
from app.api.services.user import UserService
from app.api.dependencies import get_db

user_router = APIRouter(tags=["User"])

def get_user_service(db=Depends(get_db)):
    return UserService(db)

def get_user_controller(user_service=Depends(get_user_service)):
    return UserController(user_service)

@user_router.get("/get")
async def get_all_users(user_controller: UserController = Depends(get_user_controller)):
    return await user_controller.fetch_user_controller()




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
