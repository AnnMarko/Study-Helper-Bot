from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.core.keyboards import UserFactory


router = Router()


@router.callback_query(UserFactory.filter(F.action == 'ignore'))
async def ignore(call: CallbackQuery):
    await call.answer()
