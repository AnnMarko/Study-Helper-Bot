from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.configuration import Configuration

from asyncio import sleep

from bot.core.keyboards import UserFactory
from bot.core.fsm import SupportStates
from .main import send_main_menu


router = Router()


channel_id = Configuration.channel_id


@router.callback_query(UserFactory.filter(F.action == 'support'))
async def support(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    await state.set_state(SupportStates.type_message)
    await state.set_data({"message": call.message})

    text = (
        "<b>Звернення</b> 🖋\n"
        "\n"
        "Поділіться своїм враженням про бота.\nЯкщо є пропозиції або зауваження, напишіть про них!\n"
        "\n"
        "Ми будемо Вам вдячні❤️\n"
    )
    await call.message.edit_text(text=text, reply_markup=UserFactory.support())


@router.message(SupportStates.type_message)
async def support_forward(
        message: Message,
        state: FSMContext,
):
    old_message = (await state.get_data())["message"]
    await old_message.delete_reply_markup()
    await state.clear()

    await message.answer(text="Дуже дякуємо за Ваше звернення!")
    await message.forward(chat_id=channel_id)
    await sleep(1)

    await send_main_menu(message)


@router.callback_query(SupportStates.type_message)
async def ignore(call: CallbackQuery):
    await call.answer()
