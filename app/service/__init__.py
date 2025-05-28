from service.user_service import UserService
from service.otp_service import OtpService
from service.email_service import EmailService
from service.file_service import FileService
from service.status_service import StatusService
from service.event_service import EventService
from service.mail_template_service import MailTemplateService
from service.checkout_service import CheckoutService
from service.meeting_service import MeetingService
from service.attendance_service import AttendanceService
from service.dashboard_service import DashboardService
from service.message_service import MessageService
from service.organization_service import OrganizationService
from service.guest_service import GuestService
from config import GMAIL_USERNAME, GMAIL_PASS

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
message_service = MessageService()
organization_service = OrganizationService()
guest_service = GuestService()
