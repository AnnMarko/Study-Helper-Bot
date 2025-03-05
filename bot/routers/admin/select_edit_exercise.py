from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.database import Database
from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import EditTestStates


router = Router()


async def select_edit_exercise(call, database, state):
    await state.set_state(EditTestStates.select_edit_exercise)
    test_id = (await state.get_data())["test_id"]
    await state.set_data({"test_id": test_id})

    test = await database.get_test(test_id)
    subject = test.subject
    title = test.title
    exercises_quantity = test.exercises_quantity
    is_available = test.is_available

    text = (f"<b>📃 Тест</b>\n"
            f"<i>{database._subjects[subject]}</i>\n"
            f"\n"
            f"Назва: {title}\n"
            f"\n"
            f"Кількість завдань: {exercises_quantity}\n"
            ) + (f"Доступний ✅" if is_available else f"Закритий 🚫")

    if not call.message.photo:
        await call.message.edit_text(text=text, reply_markup=AdminFactory.select_edit_exercise())
        return

    try:
        await call.message.delete()
        await call.message.answer(text=text, reply_markup=AdminFactory.select_edit_exercise())
    except TelegramBadRequest:
        await call.message.answer(text=text, reply_markup=AdminFactory.select_edit_exercise())


@router.callback_query(AdminFactory.filter(F.action == "edit_exercises"), IsAdmin())
async def edit_exercises_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    await select_edit_exercise(call, database, state)
