from fastapi import APIRouter, Depends, Path
from fastapi.security import OAuth2PasswordBearer
from typing import Any
from schemas import (
    LoginSchema,
    UserUpdateSchema,
    RegisterUserSchema,
    RemoveUserSchema,
    ForgotSchema,
    ConfirmPasswordSchema,
)
from controller import (
    validate_user_controller,
    update_user_controller,
    fetch_user_controller,
    fetch_not_attended_user_controller,
    send_mail_to_not_attended_controller,
    delete_user_data,
    insert_user_controller,
    forgot_user_controller,
    confirm_password_controller,
)
from utils import get_current_user  # your auth dependency
# from middleware import validate_schema  # if you have schema validation middleware

user_router = APIRouter(prefix="/user", tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # example for auth

@user_router.get("/get", dependencies=[Depends(get_current_user)])
async def get_all_users() -> Any:
    return await fetch_user_controller()

@user_router.get("/get-not-attended/{event_id}", dependencies=[Depends(get_current_user)])
async def get_not_attended_users(event_id: str = Path(...)):
    return await fetch_not_attended_user_controller(event_id)

@user_router.post("/save")
async def save_user(payload: RegisterUserSchema):
    # You can add extra validation middleware here if needed
    return await insert_user_controller(payload)

@user_router.post("/send-message-not-attended", dependencies=[Depends(get_current_user)])
async def send_message_not_attended():
    return await send_mail_to_not_attended_controller()

@user_router.post("/validate")
async def validate_user(payload: LoginSchema):
    return await validate_user_controller(payload)

@user_router.put("/update", dependencies=[Depends(get_current_user)])
async def update_user(payload: UserUpdateSchema):
    return await update_user_controller(payload)

@user_router.post("/forgot-password")
async def forgot_password(payload: ForgotSchema):
    return await forgot_user_controller(payload)

@user_router.post("/confirm-password")
async def confirm_password(payload: ConfirmPasswordSchema):
    return await confirm_password_controller(payload)

@user_router.delete("/delete/{user_id}", dependencies=[Depends(get_current_user)])
async def delete_user_data(user_id: str = Path(...)):
    return await delete_user_data(user_id)
