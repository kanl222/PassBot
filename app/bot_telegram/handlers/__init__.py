from aiogram import Router

__all_handlers = Router()

from .app_handlers import main_route
__all_handlers.include_routers(
    main_route,
    )
