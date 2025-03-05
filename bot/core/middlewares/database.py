from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.database import Database


class DatabaseMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session_pool: async_sessionmaker[AsyncSession] = data["session_pool"]
        async with session_pool() as session:
            data["database"] = Database(
                session_db=session,
            )

            return await handler(event, data)