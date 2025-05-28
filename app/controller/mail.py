from fastapi import HTTPException
from mail import MailTemplateBase
from service import MailTemplateService

class MailTemplateController:
    def __init__(self):
        self.service = MailTemplateService()

    async def fetch_mail_template(self, mail_template_id: str = None, submitted_by: str = None):
        try:
            data = await self.service.get_mail_template_data(mail_template_id, submitted_by)
            return data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve mailTemplate overview data: {str(e)}")

    async def insert_mail_template(self, mail_template: MailTemplateBase):
        try:
            result = await self.service.save_mail_template_data(mail_template)
            return {
                "success": True,
                "message": "Successfully added",
                "data": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Save failed: {str(e)}")

    async def update_mail_template(self, mail_template_id: str, mail_template: MailTemplateBase):
        try:
            updated = await self.service.update_mail_template_data(mail_template_id, mail_template)
            if not updated:
                raise HTTPException(status_code=404, detail="MailTemplate not found")
            return {
                "success": True,
                "message": "Successfully updated"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    async def remove_mail_template(self, mail_template_id: str):
        try:
            result = await self.service.delete_mail_template_data(mail_template_id)
            if not result:
                raise HTTPException(status_code=404, detail="MailTemplate not found")
            return {
                "success": True,
                "message": "Successfully deleted"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")
