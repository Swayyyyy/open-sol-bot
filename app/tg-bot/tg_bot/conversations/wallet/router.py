from aiogram import Router

from .menu import router as menu_router

router = Router(name="wallet")
router.include_router(menu_router)
