from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CheckoutSchema(BaseModel):
    id: Optional[str]
    user_id: str
    event_id: Optional[str]
    check_in: str
    check_out: Optional[str]
    submitted_by: str
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
