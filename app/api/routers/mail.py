from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers import MailTemplateController
from app.api.services import MailTemplateService
from app.api.dependencies import get_db

mail_template_router = APIRouter(tags=["MailTemplate"])

def get_mail_template_service(db=Depends(get_db)):
    return MailTemplateService(db)

def get_mail_template_controller(mail_template_service=Depends(get_mail_template_service)):
    return MailTemplateController(mail_template_service)

@mail_template_router.get("/get-templates")
async def get_all_mail_templates(mail_template_controller: MailTemplateController = Depends(get_mail_template_controller),
    id: Optional[str] = Query(None),
    key: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None)):
    filters = {}
    if id:
        filters["id"] = id
    if key:
        filters["key"] = key
    if organization_id:
        filters["organization_id"] = organization_id
    return await mail_template_controller.fetch_mail_template_controller(filters)

@mail_template_router.post("/save-template")
async def save_mail_template(request: Request, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    return await mail_template_controller.save_mail_template_controller(request)

@mail_template_router.put("/update-template")
async def update_mail_template(request: Request, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    return await mail_template_controller.update_mail_template_controller(request)

@mail_template_router.delete("/delete-template/{template_id}")
async def delete_mail_template(template_id: str, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    return await mail_template_controller.delete_mail_template_controller(template_id)

@mail_template_router.post("/send")
async def send_mail(request: Request, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    """
    Send email using a template by key.
    
    Request body:
    {
        "template_key": "welcome_email",  // Required: template key
        "to": "user@example.com",         // Required: recipient email
        "subject": "Custom Subject",       // Optional: override template subject
        "body": "Custom Body",             // Optional: override template body
        "user_data": {                     // Optional: user data for template variables
            "email": "user@example.com",
            "name": "John Doe",
            "firstName": "John",
            "lastName": "Doe",
            "id": "user-id"
        }
    }
    """
    return await mail_template_controller.send_mail_controller(request)

@mail_template_router.post("/send-bulk")
async def send_bulk_mail(request: Request, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    """
    Send emails to multiple users using a template by key.
    Each user will receive personalized email with their data.
    
    Request body:
    {
        "template_key": "welcome_email",  // Required: template key (e.g., "welcome", "forgot_password", "user_created_by_organization")
        "users": [                        // Required: array of user objects
            {
                "email": "user1@example.com",
                "phone": "+1234567890",
                "name": "John Doe",
                "first_name": "John",
                "last_name": "Doe",
                "id": "user-id-1"
            },
            {
                "email": "user2@example.com",
                "phone": "+1234567890",
                "name": "Jane Smith",
                "first_name": "Jane",
                "last_name": "Smith",
                "id": "user-id-2"
            }
        ],
        "extra_variables": {              // Optional: shared variables for all users
            "reset_link": "https://example.com/forgot-password?token=xxx",
            "organization_name": "Church Name",
            "expiry_time": "24 hours"
        }
    }
    
    Template variables available:
    - {{email}} - User's email address
    - {{phone}} - User's phone number
    - {{name}} - User's full name
    - {{first_name}} - User's first name
    - {{last_name}} - User's last name
    - {{reset_link}} - Password reset link (from extra_variables)
    - {{organization_name}} - Organization name (from extra_variables)
    - {{expiry_time}} - Link expiry time (from extra_variables)
    
    Available templates:
    - "welcome" - Welcome email template
    - "forgot_password" - Password reset template
    - "user_created_by_organization" - User created by organization template (includes reset password link)
    """
    return await mail_template_controller.send_bulk_mail_controller(request)

@mail_template_router.post("/send-email")
async def send_simple_email(request: Request, mail_template_controller: MailTemplateController = Depends(get_mail_template_controller)):
    """
    Send a simple email without using templates. Supports both Gmail and Amazon SES.
    
    Request body:
    {
        "to": "recipient@example.com",      // Required: recipient email address
        "subject": "Email Subject",         // Required: email subject
        "body": "Email body content",       // Required: email body/content
        "provider": "gmail",                // Optional: "gmail" or "ses" (default: "gmail")
        "from_email": "sender@example.com"  // Optional: sender email (for SES only)
    }
    
    Response (Success - 200):
    {
        "success": true,
        "message": "Email sent successfully",
        "provider": "gmail",
        "recipient": "recipient@example.com",
        "subject": "Email Subject",
        "details": {
            "message": "Email sent successfully"
        }
    }
    
    Response (Error - 400):
    {
        "success": false,
        "message": "Send email failed",
        "error": "Error message"
    }
    """
    return await mail_template_controller.send_simple_email_controller(request)

