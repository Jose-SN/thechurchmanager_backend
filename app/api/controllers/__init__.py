from .user import UserController

__all__ = ["UserController"]


# from motor.motor_asyncio import AsyncIOMotorClient
# from app.service.user import UserService
# from user import UserController
# from file import FileController
# from status import StatusController
# from event import EventController
# from mail import MailTemplateController
# from checkout import CheckoutController
# from meeting import MeetingController
# from attendance import AttendanceController
# # from webhook import WebhookController
# from dashboard import DashboardController
# from organization import OrganizationController
# from guest import GuestController

# # Setup MongoDB client and database
# client = AsyncIOMotorClient("mongodb://localhost:27017")
# db = client["thechurchmanager"]  # Use your actual DB name

# user_service = UserService(db)
# user_controller = UserController(user_service)
# # file_controller = FileController()
# # status_controller = StatusController()
# # event_controller = EventController()
# # mail_template_controller = MailTemplateController()
# # checkout_controller = CheckoutController()
# # meeting_controller = MeetingController()
# # attendance_controller = AttendanceController()
# # # webhook_controller = WebhookController()
# # dashboard_controller = DashboardController()
# # organization_controller = OrganizationController()
# # guest_controller = GuestController()
