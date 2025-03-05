from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from asyncio import sleep

from app.database import Database
from app.database.models import ExerciseModel

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import EditExerciseStates

from .select_edit_exercise import select_edit_exercise


router = Router()


async def edit_exercise_text(
        database: Database,
        exercise: ExerciseModel,
):
    number = exercise.number
    exercise_type = exercise.exercise_type
    options = exercise.options

    if exercise_type == 0:
        correct_answer = exercise.correct_answer_int
    elif exercise_type in [1, 2]:
        correct_answer = exercise.correct_answer_list
    else:
        correct_answer = exercise.correct_answer_str
    educational_material = exercise.educational_material

    if exercise_type == 1:
        options_text = (database._options_3)[options]
    elif exercise_type == 2:
        options_text = (database._options_c)[options]
    elif exercise_type == 0:
        options_text = (database._options)[options]
    else:
        options_text = ""

    if exercise_type == 0:
        answer_text = database._options_letters[correct_answer]
    elif exercise_type == 1:
        answer = [database._options_numbers[number_index] for number_index in correct_answer]
        answer_text = ", ".join(answer)
    elif exercise_type == 2:
        answer_text = ''
        for i in range(len(correct_answer)):
            answer_text += f"{database._options_numbers[i]}-{database._options_letters[correct_answer[i]]}  "
    else:
        answer_text = correct_answer

    options_available = exercise_type != 3

    text = (
               f"Завдання №{number}\n"
               f"\n"
           ) + (
               f"Тип: \t{(database._types)[exercise_type] if exercise_type is not None else '❓'}\n"
           ) + (
               f"Варіанти відповіді: \t{options_text}\n" if options_available else ""
           ) + (
               f"Правильна відповідь: \t{answer_text}\n"
           ) + (
               f"\n"
               f"Навчальний матеріал: \t{educational_material}" if educational_material is not None else ""
           )
    return text


async def edit_exercise(call, database, state):
    state_data = await state.get_data()
    exercise_id = state_data["exercise_id"]

    exercise = await database.get_exercise(exercise_id=exercise_id)
    photo = exercise.photo_id

    if exercise:
        caption = await edit_exercise_text(database, exercise)
        await call.message.answer_photo(
            caption=caption,
            photo=photo,
            reply_markup=AdminFactory.edit_chosen_exercise()
        )

    else:
        await call.message.edit_text(
            text="<i>Помилка</i> ❗️",
            reply_markup=None
        )
        await sleep(1.7)
        state_data.pop("exercise_id")
        await state.set_data(state_data)
        await select_edit_exercise(call, database, state)


async def edit_exercise_number(call, database, state):
    test_id = (await state.get_data())["test_id"]
    exercises = await database.get_all_exercises_by_test(test_id=test_id)

    if exercises:
        exercises_numbers = [exercise.number for exercise in exercises]
        exercises_numbers.sort()

        await call.message.answer(
            text="Оберіть номер завдання 🔢",
            reply_markup=AdminFactory.edit_exercise(exercises_numbers)
        )

    else:
        await call.message.answer(
            text="<i>В цьому тесті немає завдань</i> ❗️",
            reply_markup=None
        )
        await sleep(1.7)
        await select_edit_exercise(call, database, state)


@router.callback_query(AdminFactory.filter(F.action == "edit_exercise"), IsAdmin())
async def edit_exercises_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if "exercise_id" in state_data:
        state_data.pop("exercise_id")
        await state.set_data(state_data)

    await state.set_state(EditExerciseStates.edit_exercise)

    callback_data = callback_data.value

    if callback_data == 'none':
        await edit_exercise_number(call, database, state)
        return

    test_id = state_data["test_id"]
    exercise_number = int(callback_data)

    exercise = await database.get_exercise_by_number_in_test(test_id=test_id, exercise_number=exercise_number)

    if exercise:
        await state.update_data({"exercise_id": exercise.exercise_id})
        await edit_exercise(call, database, state)
    else:
        message = await call.message.answer(text=f"<i>Завдання під номером {exercise_number} не існує</i> ❗️")
        await sleep(1.7)
        await message.delete()
        await edit_exercise_number(call, database, state)


@router.callback_query(AdminFactory.filter(F.action == "delete_exercise"), IsAdmin())
async def edit_exercises_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()
    await call.message.delete()

    callback_data = callback_data.value
    if callback_data == 'none':
        await state.set_state(EditExerciseStates.delete_confirmation)
        await call.message.answer(
            text="Ви точно бажаєте видалити це завдання ❓",
            reply_markup=AdminFactory.confirm_delete_exercise()
        )
        return
    elif callback_data == '0':
        await edit_exercise(call, database, state)
        return

    state_data = await state.get_data()

    exercise_id = state_data.pop("exercise_id")
    test_id = state_data["test_id"]

    await database.delete_exercise(exercise_id=exercise_id)
    test = await database.get_test(test_id)
    exercises_quantity = test.exercises_quantity - 1
    await database.update_test(test_id, {"exercises_quantity": exercises_quantity})

    message = await call.message.answer(text="<i>Завдання видалено успішно</i> ✔️")
    await sleep(1.7)
    await message.delete()
    await edit_exercise_number(call, database, state)

"""
@router.message(EditExerciseStates.edit_exercise)
@router.message(EditExerciseStates.test_id)
@router.message(EditExerciseStates.delete_confirmation)
async def ignore_message(message: Message):
    await message.delete()


@router.message(EditExerciseStates.edit_exercise)
@router.message(EditExerciseStates.test_id)
@router.message(EditExerciseStates.delete_confirmation)
async def ignore_call(call: CallbackQuery):
    await call.answer()
"""
