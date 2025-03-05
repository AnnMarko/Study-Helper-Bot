from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from asyncio import sleep

from app.database import Database
from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import EditTestStates

from .edit_test import edit_test
from .main import admin

router = Router()


@router.callback_query(AdminFactory.filter(F.action == "delete_test"), IsAdmin())
async def delete_test_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    callback_data = callback_data.value
    if callback_data == "none":
        await state.set_state(EditTestStates.delete_confirmation)
        await call.message.edit_text(
            text='Ви точно бажаєте видалити цей тест ❓',
            reply_markup=AdminFactory.confirm_delete_test()
        )

        return

    elif callback_data == '0':
        await edit_test(call, state, database)

    else:
        test_id = (await state.get_data())["test_id"]

        await database.delete_test(test_id)
        exercises = await database.get_all_exercises_by_test(test_id=test_id)

        if exercises:
            exercises_ids = [exercise.exercise_id for exercise in exercises]
            for exercise_id in exercises_ids:
                await database.delete_exercise(exercise_id)

        await call.message.edit_text(text="Тест було видалено успішно ✔️", reply_markup=None)
        await sleep(1.7)

        await call.message.delete()
        await state.clear()
        await admin(call.message)

"""
@router.message(EditTestStates.test_id)
@router.message(EditTestStates.subject)
@router.message(EditTestStates.select_edit)
@router.message(EditTestStates.edit_test)
@router.message(EditTestStates.title_confirmation)
@router.message(EditTestStates.delete_confirmation)
@router.message(EditTestStates.select_edit_exercise)
async def ignore_message(message: Message):
    await message.delete()


@router.message(EditTestStates.test_id)
@router.message(EditTestStates.subject)
@router.message(EditTestStates.select_edit)
@router.message(EditTestStates.edit_test)
@router.message(EditTestStates.title_confirmation)
@router.message(EditTestStates.delete_confirmation)
@router.message(EditTestStates.select_edit_exercise)
@router.message(EditTestStates.edit_title)
async def ignore_call(call: CallbackQuery):
    await call.answer()
"""
