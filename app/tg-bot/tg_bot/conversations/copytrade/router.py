from aiogram import Router

from .create import router as create_router
from .edit import router as edit_router
from .menu import router as menu_router
from .tp_sl import router as tp_sl_router

router = Router(name="copytrade")
router.include_router(create_router)
router.include_router(edit_router)
router.include_router(menu_router)
router.include_router(tp_sl_router)
