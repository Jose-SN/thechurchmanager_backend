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

    async def delete_mail_template(self, mail_template_id: str) -> dict:
        result = await self.collection.find_one_and_delete({"id": ObjectId(mail_template_id)})
        if not result:
            raise HTTPException(status_code=404, detail="Mail template not found")
        return {"message": "Deleted successfully"}
