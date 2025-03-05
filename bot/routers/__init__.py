from aiogram import Dispatcher
from .user import router as user_router
from .admin import router as admin_router
from .errors import router as errors_router
from .unhandled import router as unhandled_router


def setup_routers(dispatcher: Dispatcher) -> None:
    # include routers
    dispatcher.include_routers(
        errors_router,
        user_router,
        admin_router,
        unhandled_router
    )


__all__ = [
    'setup_routers'
]
