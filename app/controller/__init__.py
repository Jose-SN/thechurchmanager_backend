from controller.user_controller import UserController
from controller.file_controller import FileController
from controller.status_controller import StatusController
from controller.event_controller import EventController
from controller.mail_template_controller import MailTemplateController
from controller.checkout_controller import CheckoutController
from controller.meeting_controller import MeetingController
from controller.attendance_controller import AttendanceController
from controller.webhook_controller import WebhookController
from controller.dashboard_controller import DashboardController
from controller.organization_controller import OrganizationController
from controller.guest_controller import GuestController

user_controller = UserController()
file_controller = FileController()
status_controller = StatusController()
event_controller = EventController()
mail_template_controller = MailTemplateController()
checkout_controller = CheckoutController()
meeting_controller = MeetingController()
attendance_controller = AttendanceController()
webhook_controller = WebhookController()
dashboard_controller = DashboardController()
organization_controller = OrganizationController()
guest_controller = GuestController()
