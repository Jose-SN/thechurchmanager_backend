from typing import List
from fastapi import HTTPException
import asyncpg
from datetime import datetime, timedelta
from app.core.config import settings
from app.api import dependencies

from app.queries.mail_template import (
    GET_MAIL_TEMPLATES_QUERY,
    GET_MAIL_TEMPLATE_BY_ID_QUERY,
    GET_MAIL_TEMPLATE_BY_KEY_QUERY,
    GET_MAIL_TEMPLATES_BY_ORGANIZATION_QUERY,
    INSERT_MAIL_TEMPLATE_QUERY,
    UPDATE_MAIL_TEMPLATE_QUERY,
    DELETE_MAIL_TEMPLATE_QUERY,
)
from app.utils.mail import send_gmail

class MailTemplateService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_mail_template_data(self, filters: dict = {}) -> List[dict]:
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters or "_id" in filters:
                    template_id = filters.get("id") or filters.get("_id")
                    template = await conn.fetchrow(GET_MAIL_TEMPLATE_BY_ID_QUERY, template_id)
                    if template:
                        return [dict(template)]
                    return []
                elif "key" in filters:
                    template = await conn.fetchrow(GET_MAIL_TEMPLATE_BY_KEY_QUERY, filters["key"])
                    if template:
                        return [dict(template)]
                    return []
                elif "organization_id" in filters:
                    rows = await conn.fetch(GET_MAIL_TEMPLATES_BY_ORGANIZATION_QUERY, filters["organization_id"])
                    return [dict(row) for row in rows]
                rows = await conn.fetch(GET_MAIL_TEMPLATES_QUERY)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Error fetching mail template data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_mail_template_data(self, template_data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                key = template_data.get("key", "")
                subject = template_data.get("subject", "")
                body = template_data.get("body", "")
                organization_id = template_data.get("organization_id")
                
                row = await conn.fetchrow(INSERT_MAIL_TEMPLATE_QUERY, key, subject, body, organization_id)
                return dict(row) if row else {}
        except Exception as e:
            print(f"❌ Error saving mail template data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_mail_template_data(self, template_data: dict) -> dict:
        template_id = template_data.get("id") or template_data.get("_id")
        if not template_id:
            raise HTTPException(status_code=400, detail="Mail Template ID is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                update_data = {k: v for k, v in template_data.items() if k not in ("_id", "id")}
                key = update_data.get("key", "")
                subject = update_data.get("subject", "")
                body = update_data.get("body", "")
                organization_id = update_data.get("organization_id")
                
                row = await conn.fetchrow(UPDATE_MAIL_TEMPLATE_QUERY, key, subject, body, organization_id, template_id)
                if not row:
                    raise ValueError("Mail Template not found")
                return dict(row)
        except ValueError:
            raise
        except Exception as e:
            print(f"❌ Error updating mail template data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_mail_template_data(self, template_id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_MAIL_TEMPLATE_QUERY, template_id)
                if result and result.startswith("DELETE"):
                    return ""
                return "Mail Template not found"
        except Exception as e:
            print(f"❌ Error deleting mail template data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def get_template_by_key(self, key: str) -> dict:
        """Get a mail template by its key"""
        try:
            async with self.db_pool.acquire() as conn:
                template = await conn.fetchrow(GET_MAIL_TEMPLATE_BY_KEY_QUERY, key)
                if not template:
                    raise HTTPException(status_code=404, detail=f"Mail template with key '{key}' not found")
                return dict(template)
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error fetching mail template by key: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    def _replace_template_variables(self, text: str, variables: dict) -> str:
        """Replace template variables like {{name}}, {{email}} in text"""
        result = text
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    async def send_mail_with_template(self, template_key: str, to: str, subject_override: str = None, body_override: str = None, user_data: dict = None, extra_variables: dict = None) -> dict:
        """
        Get a mail template by key, optionally override subject/body, and send the email.
        
        Args:
            template_key: The key of the template to use
            to: Recipient email address
            subject_override: Optional subject to override template subject
            body_override: Optional body to override template body
            user_data: Optional user data for template variable replacement
            extra_variables: Optional extra variables like reset_link, organization_name, etc.
        
        Returns:
            dict with success message
        """
        try:
            # Get template by key
            template = await self.get_template_by_key(template_key)
            
            # Use override values if provided, otherwise use template values
            subject = subject_override if subject_override is not None else template.get("subject", "")
            body = body_override if body_override is not None else template.get("body", "")
            
            # Prepare variables for replacement
            variables = {}
            
            # Add user_data variables if provided
            if user_data:
                variables.update({
                    "email": user_data.get("email", to),
                    "phone": user_data.get("phone", ""),
                    "name": user_data.get("name", "") or (user_data.get("first_name", "") + " " + user_data.get("last_name", "")).strip(),
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                })
            
            # Add extra variables if provided (like reset_link, organization_name, etc.)
            if extra_variables:
                variables.update(extra_variables)
            
            # Replace variables in subject and body if we have any variables
            if variables:
                subject = self._replace_template_variables(subject, variables)
                body = self._replace_template_variables(body, variables)
            
            # Send the email
            result = await send_gmail(to=to, subject=subject, body=body)
            return {
                "success": True,
                "message": "Email sent successfully",
                "template_key": template_key,
                "recipient": to,
                "subject": subject,
                "details": result
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error sending mail with template: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    async def send_bulk_mail_with_template(self, template_key: str, users: List[dict], extra_variables: dict = None) -> dict:
        """
        Send emails to multiple users using a template by key.
        Each user will receive the template with their personalized data (email, name, etc.)
        
        Args:
            template_key: The key of the template to use
            users: List of user objects, each should have at least 'email' field
            extra_variables: Optional extra variables like reset_link, organization_name, etc. (shared across all users)
        
        Returns:
            dict with success/failure counts and details
        """
        try:
            # Get template by key
            template = await self.get_template_by_key(template_key)
            
            results = {
                "success": True,
                "template_key": template_key,
                "total_users": len(users),
                "successful": 0,
                "failed": 0,
                "details": []
            }
            
            # Process each user
            for user in users:
                user_email = user.get("email")
                user_phone = user.get("phone")
                if not user_email:
                    results["failed"] += 1
                    results["details"].append({
                        "user": user,
                        "status": "failed",
                        "error": "Email address not found in user data"
                    })
                    continue
                
                try:
                    # Prepare variables for replacement
                    organization_name = user.get("organization", {}).get("name", "");
                    variables = {
                        "email": user_email,
                        "phone": user_phone or "",
                        "first_name": user.get("first_name", ""),
                        "last_name": user.get("last_name", ""),
                        "organization_name": organization_name,
                        "reset_link": (extra_variables.get("reset_link", "") if extra_variables else "") or (settings.THE_CHURCH_MANAGER_APP)+"/pages/authentication/forgotpassword/",
                    }
                    
                    # Add extra variables if provided (like reset_link, organization_name, etc.)
                    if extra_variables:
                        variables.update(extra_variables)
                    
                    # Replace variables in subject and body
                    subject = self._replace_template_variables(template.get("subject", ""), variables)
                    body = self._replace_template_variables(template.get("body", ""), variables)
                    
                    # Send the email
                    await send_gmail(to=user_email, subject=subject, body=body)
                    
                    results["successful"] += 1
                    results["details"].append({
                        "user": user_email,
                        "status": "success",
                    })
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "user": user_email,
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"❌ Error sending email to {user_email}: {e}")
            
            return results
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error sending bulk mail with template: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send bulk emails: {str(e)}")

