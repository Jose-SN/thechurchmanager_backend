from user import UserService
from otp import OtpService
from email import EmailService
from file import FileService
from status import StatusService
from event import EventService
from mail import MailTemplateService
from checkout import CheckoutService
from meeting import MeetingService
from attendance import AttendanceService
from dashboard import DashboardService
# from message import MessageService
from organization import OrganizationService
from guest import GuestService
from core.config import GMAIL_USERNAME, GMAIL_PASS

user_service = UserService()
otp_service = OtpService()
email_service = EmailService(GMAIL_USERNAME, GMAIL_PASS, provider='gmail')
file_service = FileService()
status_service = StatusService()
event_service = EventService()
mail_template_service = MailTemplateService()
checkout_service = CheckoutService()
meeting_service = MeetingService()
attendance_service = AttendanceService()
dashboard_service = DashboardService()
# message_service = MessageService()
organization_service = OrganizationService()
guest_service = GuestService()
