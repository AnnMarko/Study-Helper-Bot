from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.core.keyboards import UserFactory

from asyncio import sleep


router = Router()


async def send_main_menu(message: Message):
    await message.answer(
        '🔱 <b>Головне меню</b> 🔰',
        reply_markup=UserFactory.main_menu()
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        'Вітаю! 😊\n'
        '\n'
        'Я бот, який допоможе тобі у підготовці до НМТ.\n'
        'Проходь тести, щоб мати достаньо практики для складання іспитів!\n'
        '\n'
        '🤫 Також я можу допомогти тобі із завданнями, наприклад написати есе, повідомлення тощо.\n'
        'Надсилай завдання та отримуй відповідь всього за кілька хвилин!\n'
        '\n'
        'Хай щастить 🍀\n'
    )
    await sleep(0.4)
    await message.answer('📖')

    await sleep(1)
    await send_main_menu(message)


@router.callback_query(UserFactory.filter(F.action == 'main_menu'))
async def main_menu_c(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()

    await send_main_menu(call.message)

    await state.clear()


@router.message(F.text == "Меню")
async def main_menu(message: Message, state: FSMContext):
    state_data = await state.get_data()

    if "message" in state_data:
        try:
            await state_data["message"].delete()
        except TelegramBadRequest:
            pass

    await send_main_menu(message)

    await state.clear()


@router.message(Command('menu'))
async def main_menu_command(message: Message, state: FSMContext):
    state_data = await state.get_data()

    if "message" in state_data:
        try:
            await state_data["message"].delete()
        except TelegramBadRequest:
            pass

    await send_main_menu(message)

    await state.clear()

