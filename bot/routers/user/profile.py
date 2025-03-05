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


async def show_profile(message, database, user_id):
    user = await database.get_user(user_id)

    text = (
        "<b>Профіль</b> 👤\n"
        "\n"
        f"Нікнейм: {user.nickname if user.nickname else '❓'}\n"
        f"Бали: {user.points}\n"
    )
    await message.edit_text(text=text, reply_markup=UserFactory.profile())


@router.callback_query(UserFactory.filter(F.action == 'profile'))
async def profile(
        call: CallbackQuery,
        database: Database
):
    await call.answer()

    user_id = call.from_user.id
    await show_profile(call.message, database, user_id)


@router.callback_query(UserFactory.filter(F.action == 'change_nickname'))
async def change_nickname(
        call: CallbackQuery,
        state: FSMContext
):
    await call.answer()

    text = (
        "Напишіть Ваш новий нікнейм ✍️"
    )

    await call.message.edit_text(text=text, reply_markup=UserFactory.enter_nickname())

    await state.set_state(ProfileStates.enter_nickname)
    await state.set_data({"message": call.message})


@router.callback_query(UserFactory.filter(F.action == 'cancel_enter_nickname'), ProfileStates.enter_nickname)
async def cancel_enter_nickname(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await state.clear()

    user_id = call.from_user.id
    await show_profile(call.message, database, user_id)


@router.message(ProfileStates.enter_nickname)
async def enter_nickname(
        message: Message,
        database: Database,
        state: FSMContext
):
    new_nickname = message.text

    await message.delete()
    state_data = await state.get_data()
    old_message = state_data["message"]

    await state.clear()

    user_id = message.from_user.id
    await database.update_user(user_id, {"nickname": new_nickname})

    await show_profile(old_message, database, user_id)


@router.callback_query(ProfileStates.enter_nickname)
async def ignore(call: CallbackQuery):
    await call.answer()
