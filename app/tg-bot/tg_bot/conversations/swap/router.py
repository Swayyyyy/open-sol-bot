from aiogram import Router

from .swap import router as swap_router

router = Router(name="swap")
router.include_router(swap_router)
