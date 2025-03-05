from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from asyncio import sleep

from app.database import Database
from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import EditTestStates

router = Router()


async def edit_test(call, state, database):
    test_id = (await state.get_data())["test_id"]
    test = await database.get_test(test_id)
    subject = test.subject
    title = test.title
    is_available = test.is_available
    if not title:
        title = '<i>без навзви</i>'
    exercises_quantity = test.exercises_quantity

    text = (f"<b>📃 Тест</b>\n"
            f"<i>{database._subjects[subject]}</i>\n"
            f"\n"
            f"Назва: {title}\n"
            f"\n"
            f"Кількість завдань: {exercises_quantity}\n"
            ) + (f"Доступний ✅" if is_available else f"Закритий 🚫")
    await state.set_data({"test_id": test_id})
    await state.set_state(EditTestStates.edit_test)
    try:
        await call.message.edit_text(text=text, reply_markup=AdminFactory.edit_test(is_available))
    except TelegramBadRequest:
        await call.message.answer(text=text, reply_markup=AdminFactory.edit_test(is_available))


@router.callback_query(AdminFactory.filter(F.action == "edit_test"), IsAdmin())
async def edit_test_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    await edit_test(call, state, database)


@router.callback_query(AdminFactory.filter(F.action == "disable_test"), IsAdmin())
async def disable_test_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    test_id = (await state.get_data())["test_id"]
    is_available = False

    await database.update_test(test_id, {"is_available": is_available})

    await edit_test(call, state, database)


@router.callback_query(AdminFactory.filter(F.action == "enable_test"), IsAdmin())
async def enable_test_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    test_id = (await state.get_data())["test_id"]
    test = await database.get_test(test_id)
    if test.exercises_quantity > 0:
        is_available = True
        await database.update_test(test_id, {"is_available": is_available})

        await edit_test(call, state, database)


@router.callback_query(AdminFactory.filter(F.action == "edit_title"), IsAdmin())
async def edit_title_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    callback_data = callback_data.value
    if callback_data == "none":
        await state.set_state(EditTestStates.edit_title)
        await state.update_data({"message": call.message})
        await call.message.edit_text(text="Введіть нову назву ✍️", reply_markup=AdminFactory.edit_title())
        return

    elif callback_data == '0':
        await call.message.edit_text(text="Назва не була змінена ❕", reply_markup=None)
        await sleep(1.7)

        await edit_test(call, state, database)

    else:
        state_data = await state.get_data()
        test_id = state_data["test_id"]
        title = state_data["title"]

        await database.update_test(test_id, {"title": title})

        await call.message.edit_text(text="Назва була змінена успішно ✔️", reply_markup=None)
        await sleep(1.7)

        await edit_test(call, state, database)


async def title_confirmation(message, state, new_title):
    await state.set_state(EditTestStates.title_confirmation)
    await message.edit_text(
        text=f'Змінити назву на "{new_title}" ❓',
        reply_markup=AdminFactory.confirm_title()
    )


@router.message(EditTestStates.edit_title, IsAdmin())
async def enter_title(
        message: Message,
        state: FSMContext,
):
    await message.delete()
    state_data = await state.get_data()
    old_message = state_data.pop("message")
    new_title = message.text
    state_data["title"] = new_title
    await state.set_data(state_data)

    await title_confirmation(old_message, state, new_title)


@router.callback_query(EditTestStates.edit_title, IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()
