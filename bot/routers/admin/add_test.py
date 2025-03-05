from asyncio import sleep

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import AddTestStates
from bot.routers.admin.main import admin
from app.database import Database


router = Router()


@router.callback_query(AdminFactory.filter(F.action == "add_test"), IsAdmin())
async def add_test(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()
    if callback_data.value == '1':
        state_data = await state.get_data()
        await database.create_test(
            title=state_data["title"],
            subject=state_data["subject"]
        )

        await call.message.edit_text(text="Тест було додано успішно ✔️", reply_markup=None)
        await sleep(1.7)

        await call.message.delete()
        await state.clear()

    else:
        await call.message.edit_text(text="Тест не було додано ❕", reply_markup=None)
        await sleep(1.7)

        await call.message.delete()
        await state.clear()

    await admin(call.message)


async def confirmation(message, state, state_data, subject, title):
    await state.clear()
    await state.set_data(state_data)
    await state.set_state(AddTestStates.confirmation)
    await message.edit_text(
        text=(
            f"Додати цей тест?\n"
            f"\n"
            f"{subject}\n"
            f"{title}"
        ),
        reply_markup=AdminFactory.confirm_add_test()
    )


@router.callback_query(AdminFactory.filter(F.action == "no_title"), IsAdmin())
async def no_title(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    state_data = await state.get_data()
    del state_data["message"]
    state_data["title"] = ''
    subject = database._subjects[state_data['subject']]
    title = '<i>без назви</i>'

    await confirmation(call.message, state, state_data, subject, title)


@router.message(AddTestStates.title, IsAdmin())
async def enter_title(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()
    state_data = await state.get_data()
    old_message = state_data.pop("message")
    state_data["title"] = message.text
    subject = database._subjects[state_data['subject']]
    title = message.text

    await confirmation(old_message, state, state_data, subject, title)


@router.callback_query(AdminFactory.filter(F.action == 'select_subject_add_test'), IsAdmin())
async def select_subject_add_test_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext
):
    await call.answer()

    if callback_data.value == 'none':
        await state.set_state(AddTestStates.subject)

        await call.message.edit_text(text="Оберіть предмет 📚", reply_markup=AdminFactory.select_subject_add_test())
        return

    subject = callback_data.value

    await state.update_data({"subject": int(subject), "message": call.message})

    await state.set_state(AddTestStates.title)
    await call.message.edit_text(text="Введіть назву тесту ✍️", reply_markup=AdminFactory.enter_test_title())


@router.callback_query(AddTestStates.title, IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()

"""
@router.message(AddTestStates.subject)
@router.message(AddTestStates.confirmation)
async def ignore_message(message: Message):
    await message.delete()


@router.message(AddTestStates.subject)
@router.message(AddTestStates.confirmation)
@router.message(AddTestStates.title)
async def ignore_call(call: CallbackQuery):
    await call.answer()
"""
