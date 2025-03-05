from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter

from app.configuration import Configuration


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery):
        if message.from_user.id in Configuration.admins:
            return 1
        return 0
