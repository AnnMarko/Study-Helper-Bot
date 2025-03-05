from aiogram import Dispatcher

from .user import UserMiddleware
from .database import DatabaseMiddleware
# from app.configuration import Configuration


def setup_middlewares(
        dispatcher: Dispatcher,
        # config: Configuration
) -> None:
    dispatcher.update.outer_middleware(DatabaseMiddleware())
    dispatcher.update.outer_middleware(UserMiddleware())


__all__ = [
    'setup_middlewares'
]
