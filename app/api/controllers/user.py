from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.user import UserService
from fastapi.responses import JSONResponse

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def fetch_user_controller(self, filters: dict = {}):
        try:
            users = await self.user_service.get_user_data(filters)
            data = jsonable_encoder(users)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve user data",
                "error": str(err)
            })
        
    async def validate_user_controller(self, request: Request):
        body = await request.json()
        try:
            email = body.get("email")
            password = body.get("password")
            if not email or not password:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "Validation failed",
                    "error": "Email and password are required"
                })
            data = await self.user_service.login_user_data(email, password)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Validation successful",
                "data": data.dict() if hasattr(data, 'dict') else data
                })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Validation failed",
                "error": str(err)
            })
        
    async def save_user_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.user_service.save_user_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": result
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })
    async def save_bulk_user_controller(self, request: Request):
        body = await request.json()
        try:
            await self.user_service.save_bulk_user_data(body)
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

    async def login_user_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.user_service.login_user_data(body.email, body.password)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Login successful",
                "data": result
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def update_user_controller(self, request: Request):
        body = await request.json()
        try:
            await self.user_service.update_user_data(body)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": body,
                "message": "Successfully updated"
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_user_controller(self, user_id: str):
        try:
            await self.user_service.delete_user_data(user_id)
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


# from fastapi import Request, HTTPException, status
# from fastapi.responses import JSONResponse
# from bson import ObjectId
# from service import user_service, otp_service, email_service
# from utils import generate_otp
# from schemas import IUser, IValidatedUser
# from typing import Any, Dict




# from app.service.user import UserService
# from fastapi import Depends
# # from schemas.user import IUser, IValidatedUser

# class UserController:
#     def __init__(self, user_service: UserService):
#         self.user_service = user_service


    # async def confirm_password_handler(self, user_id: str, otp: int, password: str) -> dict:
    #     is_valid_otp = await otp_service.get_otp(user_id, otp)
    #     if not is_valid_otp:
    #         raise HTTPException(status_code=400, detail="Invalid OTP")

    #     # Fetch user to get email and other required fields
    #     user = await self.user_service.users.find_one({"_id": ObjectId(user_id)})
    #     if not user:
    #         raise HTTPException(status_code=400, detail="Invalid User")

    #     # Update password
    #     await self.user_service.update_user_data({"id": user_id, "password": password})
    #     jwt_payload_user = await self.user_service.generate_authorized_user(user)
    #     await otp_service.delete_otp(is_valid_otp["_id"])
    #     return jwt_payload_user.dict() if hasattr(jwt_payload_user, 'dict') else jwt_payload_user

    # async def forgot_user_handler(self, email: str) -> Dict[str, Any]:
    #     user = await user_service.fetch_user_from_email(email)
    #     if not user:
    #         raise HTTPException(status_code=404, detail="User not found")

    #     otp = int(generate_otp())
    #     otp_exists = await otp_service.get_otp(str(user["_id"]))
    #     if otp_exists:
    #         await otp_service.update_otp(str(user["_id"]), otp)
    #     else:
    #         await otp_service.save_otp(str(user["_id"]), otp)

    #     is_email_sent = await email_service.send_otp(email, otp)
    #     if not is_email_sent.get("success", False):
    #         raise HTTPException(status_code=400, detail=is_email_sent.get("error", "Failed to send OTP"))

    #     return {"userId": user["_id"], "otp": otp}

    # async def validate_user_controller(self, request: Request):
    #     body = await request.json()
    #     try:
    #         email = body.get("email")
    #         password = body.get("password")
    #         data = await self.user_service.validate_user_data(email, password)
    #         return JSONResponse(status_code=200, content=data.dict() if hasattr(data, 'dict') else data)
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Validation failed",
    #             "error": str(err)
    #         })

    # async def update_user_controller(self, request: Request):
    #     body = await request.json()
    #     try:
    #         await self.user_service.update_user_data(body)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Successfully updated"
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Update failed",
    #             "error": str(err)
    #         })

    # async def fetch_user_controller(self):
    #     try:
    #         data = await self.user_service.get_user_data()
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "data": data
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Failed to retrieve user data",
    #             "error": str(err)
    #         })

    # async def fetch_not_attended_user_controller(self, event_id: str):
    #     try:
    #         data = await user_service.get_not_attended_user_data(event_id)
    #         return JSONResponse(status_code=200, content=data)
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Failed to retrieve not attended user data",
    #             "error": str(err)
    #         })

    # async def remove_user_controller(self, user_id: str):
    #     try:
    #         await user_service.delete_user_data(user_id)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Successfully deleted"
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Delete failed",
    #             "error": str(err)
    #         })

    # async def insert_user_controller(self, request: Request):
    #     body = await request.json()
    #     try:
    #         await user_service.save_user_data(body)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Successfully added",
    #             "data": body
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Save failed",
    #             "error": str(err)
    #         })

    # async def forgot_user_controller(self, request: Request):
    #     body = await request.json()
    #     email = body.get("email")
    #     try:
    #         data = await self.forgot_user_handler(email)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Success",
    #             "data": data
    #         })
    #     except HTTPException as e:
    #         return JSONResponse(status_code=e.status_code, content={
    #             "success": False,
    #             "message": e.detail
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Error in forgot password",
    #             "error": str(err)
    #         })

    # async def confirm_password_controller(self, request: Request):
    #     body = await request.json()
    #     user_id = body.get("userId")
    #     otp = body.get("otp")
    #     password = body.get("password")
    #     try:
    #         data = await self.confirm_password_handler(user_id, otp, password)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Success",
    #             "data": data
    #         })
    #     except HTTPException as e:
    #         return JSONResponse(status_code=e.status_code, content={
    #             "success": False,
    #             "message": e.detail
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Error in forgot password",
    #             "error": str(err)
    #         })

    # async def send_mail_to_not_attended_controller(self, request: Request):
    #     body = await request.json()
    #     event_id = body.get("eventId")
    #     try:
    #         await email_service.send_message_to_non_attendees(event_id)
    #         return JSONResponse(status_code=200, content={
    #             "success": True,
    #             "message": "Successfully sent message/email to not attended users"
    #         })
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Save failed",
    #             "error": str(err)
    #         })
