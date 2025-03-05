from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory


router = Router()


@router.message(Command('admin'), IsAdmin())
async def admin(message: Message):
    await message.answer(
        text=' 🛡 <b>Панель Адміністратора </b> 🔰',
        reply_markup=AdminFactory.main_menu()
    )
