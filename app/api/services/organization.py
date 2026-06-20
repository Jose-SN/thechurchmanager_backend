from datetime import datetime, timedelta
from typing import List
import json
import logging

import asyncpg
from fastapi import HTTPException

from app.api import dependencies
from app.core.config import settings
from app.queries.organization import (
    GET_ORGANIZATIONS_QUERY,
    GET_ORGANIZATION_BY_ID_QUERY,
    GET_ORGANIZATION_BY_EMAIL_QUERY,
    GET_ORGANIZATION_BY_SUPABASE_USER_ID_QUERY,
    INSERT_ORGANIZATION_QUERY,
    UPDATE_ORGANIZATION_QUERY,
    DELETE_ORGANIZATION_QUERY,
)


class OrganizationService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _to_json(self, value, default):
        if value is None:
            return json.dumps(default)
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def _extract_fields(self, organization_data: dict) -> dict:
        contact = organization_data.get("contact") or {}
        if not isinstance(contact, dict):
            contact = {}

        return {
            "name": organization_data.get("name", ""),
            "title": organization_data.get("title", ""),
            "contact": self._to_json(contact, {}),
            "leadership": self._to_json(organization_data.get("leadership", []), []),
            "social": self._to_json(organization_data.get("social", {}), {}),
            "volunteers": self._to_json(organization_data.get("volunteers", []), []),
            "additional_information": self._to_json(
                organization_data.get("additional_information", {}), {}
            ),
            "profile_image": organization_data.get("profile_image"),
            "about": organization_data.get("about", ""),
            "members": self._to_json(organization_data.get("members", []), []),
            "password": organization_data.get("password"),
        }

    async def _find_existing(self, conn, organization_data: dict):
        organization_id = organization_data.get("id")
        if organization_id:
            row = await conn.fetchrow(GET_ORGANIZATION_BY_ID_QUERY, organization_id)
            if row:
                return row

        contact = organization_data.get("contact") or {}
        email = contact.get("email") if isinstance(contact, dict) else None
        if email:
            row = await conn.fetchrow(GET_ORGANIZATION_BY_EMAIL_QUERY, email)
            if row:
                return row

        additional_information = organization_data.get("additional_information") or {}
        supabase_user_id = (
            additional_information.get("supabase_user_id")
            if isinstance(additional_information, dict)
            else None
        )
        if supabase_user_id:
            row = await conn.fetchrow(
                GET_ORGANIZATION_BY_SUPABASE_USER_ID_QUERY, supabase_user_id
            )
            if row:
                return row

        return None

    async def get_organization_data(self, filters: dict = {}) -> List[dict]:
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_ORGANIZATION_BY_ID_QUERY, filters["id"])
                    if row:
                        return [dependencies.convert_db_types(dict(row))]
                    return []
                rows = await conn.fetch(GET_ORGANIZATIONS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"Error fetching organization data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_organization_data(self, organization_data: dict) -> dict:
        try:
            fields = self._extract_fields(organization_data)
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    INSERT_ORGANIZATION_QUERY,
                    fields["name"],
                    fields["title"],
                    fields["contact"],
                    fields["leadership"],
                    fields["social"],
                    fields["volunteers"],
                    fields["additional_information"],
                    fields["profile_image"],
                    fields["about"],
                    fields["members"],
                    fields["password"],
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except Exception as e:
            logging.error(f"Error saving organization data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def sync_organization_data(self, organization_data: dict) -> dict:
        """Create or update an organization from auth signup/login payload."""
        try:
            fields = self._extract_fields(organization_data)
            async with self.db_pool.acquire() as conn:
                existing = await self._find_existing(conn, organization_data)
                if existing:
                    row = await conn.fetchrow(
                        UPDATE_ORGANIZATION_QUERY,
                        fields["name"],
                        fields["title"],
                        fields["contact"],
                        fields["leadership"],
                        fields["social"],
                        fields["volunteers"],
                        fields["additional_information"],
                        fields["profile_image"],
                        fields["about"],
                        fields["members"],
                        fields["password"],
                        existing["id"],
                    )
                else:
                    row = await conn.fetchrow(
                        INSERT_ORGANIZATION_QUERY,
                        fields["name"],
                        fields["title"],
                        fields["contact"],
                        fields["leadership"],
                        fields["social"],
                        fields["volunteers"],
                        fields["additional_information"],
                        fields["profile_image"],
                        fields["about"],
                        fields["members"],
                        fields["password"],
                    )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error syncing organization data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_bulk_organization_data(self, organizations_data: list[dict]) -> list[dict]:
        saved = []
        for organization in organizations_data:
            saved.append(await self.sync_organization_data(organization))
        return saved

    async def login_organization_data(self, email: str, password: str):
        try:
            async with self.db_pool.acquire() as conn:
                organization = await conn.fetchrow(GET_ORGANIZATION_BY_EMAIL_QUERY, email)
                if not organization:
                    raise ValueError("No matching records found")
                return await self.generate_authorized_organization(dict(organization))
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"Error logging in organization: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def generate_authorized_organization(self, login_organization: dict):
        payload = self.get_jwt_payload(login_organization)
        expiry_seconds = dependencies.parse_expiry_to_seconds(settings.JWT_EXPIRY)
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        payload["jwt"] = "thechurchmanager"
        return payload

    def get_jwt_payload(self, login_organization: dict) -> dict:
        contact_raw = login_organization.get("contact") or {}
        if isinstance(contact_raw, str):
            try:
                contact_raw = json.loads(contact_raw)
            except json.JSONDecodeError:
                contact_raw = {}

        social_raw = login_organization.get("social") or {}
        if isinstance(social_raw, str):
            try:
                social_raw = json.loads(social_raw)
            except json.JSONDecodeError:
                social_raw = {}

        social = {
            "facebook": social_raw.get("facebook") or login_organization.get("facebook"),
            "instagram": social_raw.get("instagram") or login_organization.get("instagram"),
            "youtube": social_raw.get("youtube") or login_organization.get("youtube"),
            "twitter": social_raw.get("twitter") or login_organization.get("twitter"),
        }
        contact = {
            "phone": contact_raw.get("phone")
            or login_organization.get("phone_number")
            or login_organization.get("phone"),
            "email": contact_raw.get("email") or login_organization.get("email"),
            "website": contact_raw.get("website") or login_organization.get("website"),
            "address": contact_raw.get("address") or login_organization.get("address"),
            "officeHours": contact_raw.get("officeHours"),
        }
        return {
            "id": str(login_organization.get("id")),
            "name": login_organization.get("name"),
            "title": login_organization.get("title"),
            "members": login_organization.get("members"),
            "volunteers": login_organization.get("volunteers"),
            "about": login_organization.get("about", ""),
            "contact": contact,
            "leadership": login_organization.get("leadership", []),
            "social": social,
            "profile_image": login_organization.get("profile_image"),
            "password": login_organization.get("password"),
        }

    async def update_organization_data(self, organization_data: dict) -> dict:
        organization_id = organization_data.get("id")
        if not organization_id:
            raise HTTPException(status_code=400, detail="Organization ID is required")

        try:
            fields = self._extract_fields(organization_data)
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    UPDATE_ORGANIZATION_QUERY,
                    fields["name"],
                    fields["title"],
                    fields["contact"],
                    fields["leadership"],
                    fields["social"],
                    fields["volunteers"],
                    fields["additional_information"],
                    fields["profile_image"],
                    fields["about"],
                    fields["members"],
                    fields["password"],
                    organization_id,
                )
                if not row:
                    raise ValueError("Organization not found")
                return dependencies.convert_db_types(dict(row))
        except ValueError as err:
            return {"success": False, "error": str(err)}
        except Exception as err:
            logging.error(f"Error updating organization data: {err}")
            return {"success": False, "error": str(err)}

    async def delete_organization_data(self, organization_id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_ORGANIZATION_QUERY, organization_id)
                if result and result.startswith("DELETE"):
                    return ""
                return "Organization not found"
        except Exception as e:
            logging.error(f"Error deleting organization data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
