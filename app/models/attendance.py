# db/models.py
from odmantic import Model, Field
from datetime import datetime

class Attendance(Model):
    parentId: str
    parentType: str
    questionId: str
    attendance: str = None
    submittedBy: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)
