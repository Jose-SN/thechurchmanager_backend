from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime

class Checkout(Document):
    user_id = ReferenceField('User', required=True)
    event_id = ReferenceField('Event', required=False)
    check_in = StringField(required=True)
    check_out = StringField(required=False)
    submitted_by = ReferenceField('User', required=True)
    creation_date = DateTimeField(default=datetime.utcnow)
    modification_date = DateTimeField(default=datetime.utcnow)
