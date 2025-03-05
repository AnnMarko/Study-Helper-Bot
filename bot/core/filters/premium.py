from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter

from app.configuration import Configuration
from app.database import Database


class IsPremium(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, database: Database):
        # if message.from_user.id in Configuration.admins:
        #     return 1
        return (await database.get_user(message.from_user.id)).gpt_premium


async def is_premium(user_id: int, database: Database):
    # if user_id in Configuration.admins:
    #     return 1
    return (await database.get_user(user_id)).gpt_premium
