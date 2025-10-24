from .user import UserService
from .team import TeamService
from .role import RoleService
from .module import ModuleService
from .organization import OrganizationService
from .teacher import TeacherService
from .inventory import InventoryService

__all__ = [
    "UserService", 
    "TeamService", 
    "RoleService", 
    "ModuleService", 
    "OrganizationService",
    "TeacherService",
    "InventoryService"
    ]


# from otp import OtpService
# from email import EmailService
# from file import FileService
# from status import StatusService
# from event import EventService
# from mail import MailTemplateService
# from checkout import CheckoutService
# from meeting import MeetingService
# from attendance import AttendanceService
# from dashboard import DashboardService
# # from message import MessageService
# from organization import OrganizationService
# from guest import GuestService
# from core.config import GMAIL_USERNAME, GMAIL_PASS

# from fastapi import Depends, Request
# from app.service.user import UserService
# from app.routers import get_db

# def get_user_service(db=Depends(get_db)):
#     return UserService(db)
# otp_service = OtpService()
# email_service = EmailService(GMAIL_USERNAME, GMAIL_PASS, provider='gmail')
# file_service = FileService()
# status_service = StatusService()
# event_service = EventService()
# mail_template_service = MailTemplateService()
# checkout_service = CheckoutService()
# meeting_service = MeetingService()
# attendance_service = AttendanceService()
# dashboard_service = DashboardService()
# # message_service = MessageService()
# organization_service = OrganizationService()
# guest_service = GuestService()
