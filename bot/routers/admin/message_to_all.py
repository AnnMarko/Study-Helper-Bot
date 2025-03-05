from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm.admin import MessageToAllStates
from .main import admin

from app.database import Database

from asyncio import sleep


router = Router()


@router.callback_query(AdminFactory.filter(F.action == 'send_message_to_all'), IsAdmin())
async def send_message_to_all(
        call: CallbackQuery,
        state: FSMContext,
):
    await state.set_state(MessageToAllStates.type_message)
    await state.set_data({"message": call.message})

    await call.message.edit_text(
        text='Напишіть повідомлення, яке отримають <b>УСІ</b> учасники ✍️',
        reply_markup=AdminFactory.send_message_to_all()
    )


@router.message(MessageToAllStates.type_message, IsAdmin())
async def type_message(
        message: Message,
        state: FSMContext,
):
    old_message = (await state.get_data())["message"]
    await message.delete()

    await state.clear()
    await state.set_state(MessageToAllStates.send_confirmation)

    message_text = message.caption if message.photo else message.text

    await state.set_data({"message_text": message_text})

    text = (
        f"{message_text}\n"
        f"\n"
        f"Бажаєте надіслати це повідомлення всім учасникам ❓"
    )

    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data({"photo_id": photo_id})
        await old_message.delete()

        await message.answer_photo(
            text=text,
            photo=photo_id,
            caption=text,
            reply_markup=AdminFactory.confirm_send_message_to_all()
        )
        return

    await old_message.edit_text(text=text, reply_markup=AdminFactory.confirm_send_message_to_all())


@router.callback_query(AdminFactory.filter(F.action == 'do_send_message_to_all'), IsAdmin())
async def send_message_to_all(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
        bot: Bot,
):
    state_data = await state.get_data()

    if callback_data.value == "0":
        await call.message.delete()

        temporary_message = await call.message.answer(text='Повідомлення НЕ БУЛО надіслано ❗️')
        await sleep(1.7)
        await temporary_message.delete()
    else:
        message_text = state_data["message_text"]

        all_users = await database.get_all_users()
        all_users_ids = [user.user_id for user in all_users]

        for user_id in all_users_ids:
            if "photo_id" in state_data:
                photo_id = state_data["photo_id"]
                await bot.send_photo(chat_id=user_id, photo=photo_id, caption=message_text)
            else:
                await bot.send_message(chat_id=user_id, text=message_text)
        await call.message.delete_reply_markup()

        await call.message.answer(text='Повідомлення надіслано ❗️')
        await sleep(1.7)

    await state.clear()
    await admin(call.message)


@router.callback_query(MessageToAllStates.type_message, IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()
