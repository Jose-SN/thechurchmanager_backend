from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .root import root_router
from fastapi import APIRouter
from .user import user_router
from .team import team_router
from .role import role_router
from .module import module_router
from .organization import organization_router
from .teacher import teacher_router
from .inventory import inventory_router
from .plan import plan_router
from .permission import permission_router
from .file import file_router
from .user_role import user_role_router
from .mail import mail_template_router
from .classes import class_router
from .student import student_router
from .account import account_router
from .song import song_router
from .rota import rota_router
from .rota_song import rota_song_router
from .expense import expense_router
from .health import router as health_router  # rename the file if needed

router = APIRouter()

router.include_router(health_router, prefix="/health-check")
router.include_router(user_router, prefix="/user")
router.include_router(team_router, prefix="/team")
router.include_router(module_router, prefix="/module")
router.include_router(role_router, prefix="/role")
router.include_router(plan_router, prefix="/plan")
router.include_router(organization_router, prefix="/organization")
router.include_router(teacher_router, prefix="/teacher")
router.include_router(inventory_router, prefix="/inventory")
router.include_router(permission_router, prefix="/permission")
router.include_router(file_router, prefix="/file")
router.include_router(user_role_router, prefix="/user-role")
router.include_router(mail_template_router, prefix="/mail")
router.include_router(class_router, prefix="/class")
router.include_router(student_router, prefix="/student")
router.include_router(account_router, prefix="/account")
router.include_router(song_router, prefix="/song")
router.include_router(rota_router, prefix="/rota")
router.include_router(rota_song_router, prefix="/rota-song")
router.include_router(expense_router, prefix="/expense")
router.include_router(root_router)

