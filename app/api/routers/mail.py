from fastapi import APIRouter, Depends
from controllers import (
    fetch_mail_templates,
    insert_mail_template,
    update_mail_template,
    remove_mail_template
)
from utils import get_current_user
from utils import validate_mail_template

mail_template_router = APIRouter(prefix="/mailTemplate")

# GET /mailTemplate/get - Get all mail templates
@mail_template_router.get("/get")
async def get_mail_templates():
    return await fetch_mail_templates()

# POST /mailTemplate/save - Save a new mail template
@mail_template_router.post("/save", dependencies=[Depends(get_current_user)])
async def save_mail_template(payload: dict = Depends(validate_mail_template)):
    return await insert_mail_template(payload)

# PUT /mailTemplate/update - Update a mail template
@mail_template_router.put("/update", dependencies=[Depends(get_current_user)])
async def update_mail_template(payload: dict = Depends(validate_mail_template)):
    return await update_mail_template(payload)

# DELETE /mailTemplate/delete/{mail_template_id} - Delete a mail template
@mail_template_router.delete("/delete/{mail_template_id}", dependencies=[Depends(get_current_user)])
async def delete_mail_template(mail_template_id: str):
    return await remove_mail_template(mail_template_id)
