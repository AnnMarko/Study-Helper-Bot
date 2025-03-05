from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from asyncio import sleep


from app.database import Database
from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import EditTestStates

from .main import admin


router = Router()


async def get_all_tests(database, state):
    subject = (await state.get_data())["subject"]
    tests = await database.get_all_tests_by_subject(subject=subject)
    if not tests:
        return False

    tests_ids = [item.test_id for item in tests]
    tests_ids.reverse()

    await state.update_data({"tests_ids": tests_ids})
    return True


async def select_test_to_edit(message, database, state):
    state_data = await state.get_data()

    index = state_data["current_test_index"]
    tests_ids = state_data["tests_ids"]

    test_id = tests_ids[index]

    test = await database.get_test(test_id=test_id)
    title = test.title
    subject = test.subject
    exercises_quantity = test.exercises_quantity
    is_available = test.is_available

    title_text = f"{title}\n" if title else ""
    await state.update_data({"current_test_id": test_id, "current_test_index": index})
    text = (f"<b>📃 Тести</b>\n"
            f"<i>{database._subjects[subject]}</i>\n"
            f"\n"
            f"{title_text}"
            f"\n"
            f"Кількість завдань: {exercises_quantity}\n"
            f"{'Доступний ✅' if is_available else 'Закритий 🚫'}"
            )
    await message.edit_text(text=text, reply_markup=AdminFactory.select_test_to_edit(len(tests_ids), index))


async def select_subject_edit_test(call, state):
    await state.set_state(EditTestStates.subject)

    await call.message.edit_text(
        text="Оберіть предмет тесту для редагування 📚",
        reply_markup=AdminFactory.select_subject_edit_test()
    )


@router.callback_query(AdminFactory.filter(F.action == 'select_subject_edit_test'), IsAdmin())
async def select_subject_edit_test_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    if callback_data.value == 'none':
        await select_subject_edit_test(call, state)
        return

    subject = callback_data.value

    await state.update_data({"subject": int(subject), "current_test_index": 0})

    result = await get_all_tests(database, state)

    if not result:
        await call.message.edit_text(text="З цього предмета немає тестів ❗️")
        await sleep(1.7)
        await state.clear()
        await select_subject_edit_test(call, state)
        return

    await state.set_state(EditTestStates.test_id)
    await select_test_to_edit(call.message, database, state)


async def select_edit(call, database, state):
    state_data = await state.get_data()

    if "test_id" not in state_data:
        await call.message.delete()
        await admin(call.message)
        return

    test_id = state_data["test_id"]

    test = await database.get_test(test_id)
    title = test.title
    exercises_quantity = test.exercises_quantity
    is_available = test.is_available
    subject = test.subject

    text = (f"<b>📃 Тест</b>\n"
            f"<i>{database._subjects[subject]}</i>\n"
            f"\n"
            f"Назва: {title}\n"
            f"\n"
            f"Кількість завдань: {exercises_quantity}\n"
            ) + (f"Доступний ✅" if is_available else f"Закритий 🚫")
    await call.message.edit_text(text=text, reply_markup=AdminFactory.select_edit())


@router.callback_query(AdminFactory.filter(F.action == "select_edit"), IsAdmin())
async def select_edit_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()

    await state.set_state(EditTestStates.select_edit)
    await select_edit(call, database, state)


@router.callback_query(AdminFactory.filter(F.action == 'select_test_to_edit'), IsAdmin())
async def select_test_nmt_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
) -> None:
    await call.answer()

    state_data = await state.get_data()
    call_data = callback_data.value
    if call_data == "select":
        test_id = state_data["current_test_id"]

        await state.clear()
        await state.set_state(EditTestStates.select_edit)
        await state.update_data({"test_id": test_id})

        await select_edit(call, database, state)

    elif call_data == "back":
        await state.clear()
        await select_subject_edit_test(call, state)

    elif call_data == "go_back":
        index = state_data["current_test_index"] - 1
        await state.update_data({"current_test_index": index})
        await select_test_to_edit(call.message, database, state)

    elif call_data == "go_back_five":
        index = state_data["current_test_index"] - 5
        if index < 0:
            index = 0
        await state.update_data({"current_test_index": index})
        await select_test_to_edit(call.message, database, state)

    elif call_data == "go_forward":
        index = state_data["current_test_index"] + 1
        await state.update_data({"current_test_index": index})
        await select_test_to_edit(call.message, database, state)

    elif call_data == "go_forward_five":
        index = state_data["current_test_index"] + 5
        tests_ids = state_data["tests_ids"]
        if index >= len(tests_ids):
            index = len(tests_ids) - 1
        await state.update_data({"current_test_index": index})
        await select_test_to_edit(call.message, database, state)

