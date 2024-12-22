from aiogram import Router
from .common import common_router
from .admin import admin_router
from .student import student_router
from .teacher import teacher_router
from .auth import auth_router

__all_routes: Router = Router()
__all_routes.include_routers(common_router,
                             teacher_router,
                             admin_router,
                             student_router,
                             auth_router,
                             )
