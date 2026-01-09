from fastapi import Request
from fastapi.encoders import jsonable_encoder
from app.api.services.mail import MailTemplateService
from fastapi.responses import JSONResponse

class MailTemplateController:
    def __init__(self, mail_template_service: MailTemplateService):
        self.mail_template_service = mail_template_service

    async def fetch_mail_template_controller(self, filters: dict = {}):
        try:
            templates = await self.mail_template_service.get_mail_template_data(filters)
            data = jsonable_encoder(templates)
            return JSONResponse(status_code=200, content={
                "success": True,
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Failed to retrieve mail template data",
                "error": str(err)
            })

    async def save_mail_template_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.mail_template_service.save_mail_template_data(body)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully added",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Save failed",
                "error": str(err)
            })

    async def update_mail_template_controller(self, request: Request):
        body = await request.json()
        try:
            result = await self.mail_template_service.update_mail_template_data(body)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Successfully updated",
                "data": data
            })
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Update failed",
                "error": str(err)
            })

    async def delete_mail_template_controller(self, template_id: str):
        try:
            await self.mail_template_service.delete_mail_template_data(template_id)
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

    # async def send_mail_controller(self, request: Request):
    #     """Send email using a template by key, with optional content overrides"""
    #     body = await request.json()
    #     try:
    #         template_key = body.get("template_key")
    #         to = body.get("to")
    #         subject_override = body.get("subject")  # Optional override
    #         body_override = body.get("body")  # Optional override
    #         user_data = body.get("user_data")  # Optional user data for template variables
    #         extra_variables = body.get("extra_variables")  # Optional extra variables like reset_link, organization_name
            
    #         if not template_key:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "template_key is required"
    #             })
            
    #         if not to:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "to (recipient email) is required"
    #             })
            
    #         result = await self.mail_template_service.send_mail_with_template(
    #             template_key=template_key,
    #             to=to,
    #             subject_override=subject_override,
    #             body_override=body_override,
    #             user_data=user_data,
    #             extra_variables=extra_variables
    #         )
    #         return JSONResponse(status_code=200, content=result)
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Send mail failed",
    #             "error": str(err)
    #         })

    # async def send_bulk_mail_controller(self, request: Request):
    #     """Send emails to multiple users using a template by key"""
    #     body = await request.json()
    #     try:
    #         template_key = body.get("template_key")
    #         users = body.get("users", [])
    #         extra_variables = body.get("extra_variables")  # Optional extra variables like reset_link, organization_name
            
    #         if not template_key:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "template_key is required"
    #             })
            
    #         if not users or not isinstance(users, list):
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "users (array of user objects) is required"
    #             })
            
    #         result = await self.mail_template_service.send_bulk_mail_with_template(
    #             template_key=template_key,
    #             users=users,
    #             extra_variables=extra_variables
    #         )
    #         return JSONResponse(status_code=200, content=result)
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Send bulk mail failed",
    #             "error": str(err)
    #         })

    # async def send_simple_email_controller(self, request: Request):
    #     """Send a simple email without using templates. Supports both Gmail and SES."""
    #     try:
    #         # Parse JSON with error handling
    #         try:
    #             body = await request.json()
    #         except ValueError as json_err:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "Invalid JSON in request body. Please ensure the request body contains valid JSON.",
    #                 "error": str(json_err)
    #             })
            
    #         if not body:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "Request body is required"
    #             })
            
    #         to = body.get("to")
    #         subject = body.get("subject")
    #         email_body = body.get("body")
    #         provider = body.get("provider", "gmail")  # Default to gmail
    #         from_email = body.get("from_email")  # Optional, for SES
            
    #         if not to:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "to (recipient email) is required"
    #             })
            
    #         if not subject:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "subject is required"
    #             })
            
    #         if not email_body:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "body is required"
    #             })
            
    #         if provider.lower() not in ["gmail", "ses"]:
    #             return JSONResponse(status_code=400, content={
    #                 "success": False,
    #                 "message": "provider must be either 'gmail' or 'ses'"
    #             })
            
    #         result = await self.mail_template_service.send_simple_email(
    #             to=to,
    #             subject=subject,
    #             body=email_body,
    #             provider=provider,
    #             from_email=from_email
    #         )
    #         return JSONResponse(status_code=200, content=result)
    #     except Exception as err:
    #         return JSONResponse(status_code=400, content={
    #             "success": False,
    #             "message": "Send email failed",
    #             "error": str(err)
    #         })


    async def send_email_gmail_controller(self, request: Request):
        """Send an email using Gmail SMTP"""
        try:
            # Parse JSON with error handling
            try:
                request_body = await request.json()
            except ValueError as json_err:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "Invalid JSON in request body. Please ensure the request body contains valid JSON.",
                    "error": str(json_err)
                })
            
            if not request_body:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "Request body is required"
                })
            
            to = request_body.get("to")
            subject = request_body.get("subject")
            email_body = request_body.get("body")
            html = request_body.get("html", False)
            
            if not to:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "to (recipient email) is required"
                })
            
            if not subject:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "subject is required"
                })
            
            if not email_body:
                return JSONResponse(status_code=400, content={
                    "success": False,
                    "message": "body is required"
                })
            
            result = await self.mail_template_service.send_email_gmail(to=to, subject=subject, body=email_body, html=html)
            data = jsonable_encoder(result)
            return JSONResponse(status_code=200, content=data)
        except Exception as err:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Send failed",
                "error": str(err)
            })
