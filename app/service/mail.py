from typing import List, Optional
from models.mail_template import MailTemplate, MailTemplateCreate
from pymongo.collection import Collection
from bson import ObjectId
from fastapi import HTTPException

class MailTemplateService:
    def __init__(self, db_collection: Collection):
        self.collection = db_collection

    async def get_mail_templates(self, mail_template_id: Optional[str] = None, submitted_by: Optional[str] = None) -> List[dict]:
        if mail_template_id:
            result = await self.collection.find_one({"_id": ObjectId(mail_template_id)})
            if not result:
                raise HTTPException(status_code=404, detail="Mail template not found")
            return result
        elif submitted_by:
            cursor = self.collection.find({"submittedBy": submitted_by})
        else:
            cursor = self.collection.find()
        return await cursor.to_list(length=100)

    async def save_mail_template(self, data: MailTemplateCreate) -> dict:
        result = await self.collection.insert_one(data.dict())
        new_template = await self.collection.find_one({"_id": result.inserted_id})
        return new_template

    async def update_mail_template(self, mail_template_id: str, data: MailTemplateCreate) -> dict:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(mail_template_id)},
            {"$set": data.dict()},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Mail template not found")
        return result

    async def delete_mail_template(self, mail_template_id: str) -> dict:
        result = await self.collection.find_one_and_delete({"_id": ObjectId(mail_template_id)})
        if not result:
            raise HTTPException(status_code=404, detail="Mail template not found")
        return {"message": "Deleted successfully"}
