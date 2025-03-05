from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.configuration import Configuration
from app.database import Database

from asyncio import sleep

from bot.core.keyboards import UserFactory
from bot.core.fsm import ProfileStates
from .main import send_main_menu


router = Router()


@router.callback_query(UserFactory.filter(F.action == 'leaderboard'))
async def profile(
        call: CallbackQuery,
        database: Database
):
    await call.answer()
    user_id = call.from_user.id
    user = await database.get_user(user_id)

    if not user.nickname:
        text = "Щоб подивитись таблицю лідерів необхідно написати свій нікнейм у вкладці «Профіль 👤»"
    else:
        top_50_users = await database.get_50_best_users()
        text = "<b>Таблиця лідерів</b> 🏆\n\n"

        for i in range(len(top_50_users)):
            text += f"<b>{i + 1}.</b> {top_50_users[i].nickname}:\t<b>{top_50_users[i].points}</b>\n"

    await call.message.edit_text(text=text, reply_markup=UserFactory.leaderboard())
