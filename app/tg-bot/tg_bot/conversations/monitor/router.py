from aiogram import Router

from .create import router as create_router
from .edit import router as edit_router
from .menu import router as menu_router

router = Router(name="monitor")
router.include_router(menu_router)
router.include_router(create_router)
router.include_router(edit_router)
