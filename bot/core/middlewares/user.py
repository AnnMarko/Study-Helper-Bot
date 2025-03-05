from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Chat, TelegramObject, User as TelegramUser
from aiogram import Bot

from app.configuration import Configuration
from app.database import Database


class UserMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        # get data from eventz
        event_user: TelegramUser = data["event_from_user"]
        database: Database = data['database']
        config: Configuration = data["config"]
        bot: Bot = data["bot"]
        # delete
        if "event_chat" in data:
            chat: Chat = data["event_chat"]
        #

        data["admin"] = event_user.id in config.admins

        # get user from the database
        user = await database.get_user(user_id=event_user.id)
        if not user:
            # create new user
            user = await database.create_user(
                telegram_user=event_user,
            )
        # delete
        if event_user.id not in config.admins:
            await bot.send_message(chat_id=chat.id, text="Вибачте, але бот поки що в розробці🧑‍💻")
            return
        #
        # update data and return handler
        data["user"] = user
        return await handler(event, data)
