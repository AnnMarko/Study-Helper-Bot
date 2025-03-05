from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from .main import admin


router = Router()


@router.callback_query(AdminFactory.filter(F.action == 'ignore'), IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()


@router.callback_query(AdminFactory.filter(F.action == 'cancel'), IsAdmin())
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await admin(call.message)

