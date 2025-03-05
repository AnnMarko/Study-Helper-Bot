from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from asyncio import sleep

from bot.core.keyboards import UserFactory
from bot.core.fsm import NMTStates
from app.database import Database

from .main import send_main_menu


router = Router()


async def exercise_form(message: Message, database: Database, state: FSMContext, user_id=None):
    state_data = await state.get_data()
    exercises_ids = state_data["exercises_ids"]

    test_id = state_data["test_id"]
    test = await database.get_test(test_id)

    if not exercises_ids:
        user = await database.get_user(user_id)
        test_subject = test.subject

        match test_subject:
            case 0:
                user_tests_done = user.ukr_tests_done
                user_tests_done.append(test_id)
                await database.update_user(user_id, {"ukr_tests_done": user_tests_done})
            case 1:
                user_tests_done = user.math_tests_done
                user_tests_done.append(test_id)
                await database.update_user(user_id, {"math_tests_done": user_tests_done})
            case 2:
                user_tests_done = user.hist_tests_done
                user_tests_done.append(test_id)
                await database.update_user(user_id, {"hist_tests_done": user_tests_done})

        await message.answer(text="Вітаю!🥳\nВи склали цей тест!")
        await sleep(0.4)
        await message.answer(text="🎉")

        await sleep(0.9)

        await state.clear()
        await send_main_menu(message)
        return

    exercise_id = exercises_ids[0]

    exercise = await database.get_exercise(exercise_id)
    exercise_type = exercise.exercise_type
    exercise_photo = exercise.photo_id
    exercise_options = exercise.options

    exercises_quantity = test.exercises_quantity

    exercises_done_text = f"Завдань виконано: <b>{exercises_quantity - len(exercises_ids)}/{exercises_quantity}</b>"

    if exercise_type == 0:
        options_len = int(database._options[exercise_options])
        data = {k: v for k, v in database._options_letters.items() if k < options_len}
        if "selected" in state_data:
            selected = state_data["selected"]
        else:
            selected = []
            await state.update_data({"selected": selected})

        reply_markup = UserFactory.exercise_options(data, selected)
    elif exercise_type == 1:
        options_len = int(database._options_3[exercise_options])
        data = {k: v for k, v in database._options_numbers.items() if k < options_len}
        if "selected" in state_data:
            selected = state_data["selected"]
        else:
            selected = []
            await state.update_data({"selected": selected})

        reply_markup = UserFactory.exercise_options_3(data, selected)
    elif exercise_type == 2:
        numbers_len, letters_len = (database._options_c[exercise_options]).split(":")
        numbers_len = int(numbers_len)
        letters_len = int(letters_len)

        if "selected" in state_data:
            selected = state_data["selected"]
        else:
            selected = {}
            await state.update_data({"selected": selected})

        is_done = len(selected) == numbers_len
        letters = {k: v for k, v in database._options_letters.items() if k < letters_len}
        numbers = {k: v for k, v in database._options_numbers.items() if k < numbers_len}

        reply_markup = UserFactory.exercise_options_c(letters, numbers, selected, is_done)
    else:
        await state.set_state(NMTStates.type_answer)

        caption = (
            "Напишіть свою відповідь\n\n<i>Приклад правильного запису:\n3,4    2/3\n"
            f"Приклад неправильного запису:\n3.4    2 / 3</i>\n\n{exercises_done_text}"
        )
        reply_markup = UserFactory.cancel_answer()

        message = await message.answer_photo(photo=exercise_photo, caption=caption, reply_markup=reply_markup)
        await state.update_data({"message": message})
        return

    try:
        await message.edit_reply_markup(reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer_photo(photo=exercise_photo, caption=exercises_done_text, reply_markup=reply_markup)


async def check_option(state, database, call):
    state_data = await state.get_data()
    selected = state_data.pop("selected")

    test_id = state_data["test_id"]
    test = await database.get_test(test_id)
    exercises_quantity = test.exercises_quantity

    exercises_ids = state_data["exercises_ids"]
    exercise_id = exercises_ids.pop(0)
    exercise = await database.get_exercise(exercise_id)
    exercise_photo = exercise.photo_id
    exercise_type = exercise.exercise_type
    exercise_educational_material = exercise.educational_material

    match exercise_type:
        case 0:
            exercise_answer = exercise.correct_answer_int
        case _:
            exercise_answer = exercise.correct_answer_list

    if exercise_type == 0:
        answer = selected[0]
    elif exercise_type == 2:
        answer = list(selected.values())
    else:
        answer = selected

    if exercise_type == 1:
        answer.sort()
        exercise_answer.sort()

    if exercise_answer == answer:
        state_data["exercises_ids"] = exercises_ids

        test_id = state_data["test_id"]
        test = await database.get_test(test_id)
        test_subject = test.subject

        user_id = call.from_user.id
        user = await database.get_user(user_id)

        match test_subject:
            case 0:
                exercises_done_ids = user.ukr_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"ukr_exercises_done": exercises_done_ids})
            case 1:
                exercises_done_ids = user.math_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"math_exercises_done": exercises_done_ids})
            case 2:
                exercises_done_ids = user.hist_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"hist_exercises_done": exercises_done_ids})

        if exercise_type == 0:
            answer_text = database._options_letters[exercise_answer]
        elif exercise_type == 1:
            answer = [database._options_numbers[number_index] for number_index in exercise_answer]
            answer_text = ", ".join(answer)
        else:
            answer_text = ''
            for i in range(len(exercise_answer)):
                answer_text += f"{database._options_numbers[i]}-{database._options_letters[exercise_answer[i]]}  "
        exercises_done_text = f"Завдань виконано: <b>{exercises_quantity - len(exercises_ids)}/{exercises_quantity}</b>"
        caption = f"Чудово! Правильна відповідь — {answer_text}\n\n{exercises_done_text}"

        user_points = user.points + 5
        await database.update_user(user_id, {"points": user_points})

    else:
        exercises_ids.append(exercise_id)
        state_data["exercises_ids"] = exercises_ids
        exercises_done_text = f"Завдань виконано: <b>{exercises_quantity - len(exercises_ids)}/{exercises_quantity}</b>"
        caption = f"На жаль, ні 😥\nСпробуйте наступного разу\n\n{exercises_done_text}"

    await state.set_data(state_data)
    reply_markup = UserFactory.correct_answer(exercise_educational_material, exercise_id)
    try:
        await call.message.edit_caption(caption=caption)
        await call.message.edit_reply_markup(reply_markup=reply_markup)
    except TelegramBadRequest:
        await call.message.answer_photo(
            photo=exercise_photo,
            caption=caption,
            reply_markup=reply_markup
        )


async def get_exercises(call: CallbackQuery, database: Database, state: FSMContext):
    await state.set_state(NMTStates.proceed_test)
    state_data = await state.get_data()
    test_id = state_data["test_id"]

    exercises = await database.get_all_exercises_by_test(test_id)
    exercises_ids = [exercise.exercise_id for exercise in exercises]

    user_id = call.from_user.id
    user = await database.get_user(user_id)
    test = await database.get_test(test_id)

    match test.subject:
        case 0:
            exercises_done_ids = user.ukr_exercises_done
        case 1:
            exercises_done_ids = user.math_exercises_done
        case 2:
            exercises_done_ids = user.hist_exercises_done
        case _:
            exercises_done_ids = []

    exercises_ids = [item for item in exercises_ids if item not in exercises_done_ids]

    await state.update_data({"exercises_ids": exercises_ids})
    await exercise_form(call.message, database, state, user_id)
    return


@router.callback_query(UserFactory.filter(F.action == "proceed_nmt_next"))
async def exercise_options_call(
        call: CallbackQuery,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    user_id = call.from_user.id
    await exercise_form(call.message, database, state, user_id)


@router.callback_query(UserFactory.filter(F.action == "check_option"))
async def check_option_call(
        call: CallbackQuery,
        state: FSMContext,
        database: Database,
):
    await call.answer()

    await check_option(state, database, call)


@router.callback_query(UserFactory.filter(F.action == "exercise_options"))
async def exercise_options_call(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()

    state_data = await state.get_data()
    selected_old = state_data["selected"]

    if int(callback_data.value) in selected_old:
        selected = []
    else:
        selected = [int(callback_data.value)]

    await state.update_data({"selected": selected})

    await exercise_form(call.message, database, state)


@router.callback_query(UserFactory.filter(F.action == "exercise_options_3"))
async def exercise_options_3_call(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()

    state_data = await state.get_data()
    selected = state_data["selected"]

    if int(callback_data.value) in selected:
        selected.remove(int(callback_data.value))
    else:
        selected.append(int(callback_data.value))

    if len(selected) > 3:
        selected.pop(0)

    await state.update_data({"selected": selected})

    await exercise_form(call.message, database, state)


@router.callback_query(UserFactory.filter(F.action == "exercise_options_c"))
async def exercise_options_c_call(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()

    state_data = await state.get_data()
    selected = state_data["selected"]

    new_number, new_letter = callback_data.value.split('-')
    new_number = int(new_number)
    new_letter = int(new_letter)

    selected[new_number] = new_letter

    await state.update_data({"selected": selected})
    await exercise_form(call.message, database, state)


@router.message(NMTStates.type_answer)
async def type_answer(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()
    await state.set_state(NMTStates.proceed_test)
    state_data = await state.get_data()

    test_id = state_data["test_id"]
    test = await database.get_test(test_id)
    exercises_quantity = test.exercises_quantity

    answer = message.text

    old_message = state_data.pop("message")
    await old_message.delete()

    exercises_ids = state_data["exercises_ids"]
    exercise_id = exercises_ids[0]
    exercise = await database.get_exercise(exercise_id)
    exercise_photo = exercise.photo_id
    exercise_answer = exercise.correct_answer_str
    exercise_educational_material = exercise.educational_material

    if exercise_answer == answer:
        exercises_ids.pop(0)
        state_data["exercises_ids"] = exercises_ids

        test_id = state_data["test_id"]
        test = await database.get_test(test_id)
        test_subject = test.subject

        user_id = message.from_user.id
        user = await database.get_user(user_id)

        match test_subject:
            case 0:
                exercises_done_ids = user.ukr_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"ukr_exercises_done": exercises_done_ids})
            case 1:
                exercises_done_ids = user.math_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"math_exercises_done": exercises_done_ids})
            case 2:
                exercises_done_ids = user.hist_exercises_done
                exercises_done_ids.append(exercise_id)
                await database.update_user(user_id, {"hist_exercises_done": exercises_done_ids})

        exercises_done_text = f"Завдань виконано: <b>{exercises_quantity - len(exercises_ids)}/{exercises_quantity}</b>"
        caption = f"Чудово! Правильна відповідь — {exercise_answer}\n\n{exercises_done_text}"

        user_points = user.points + 5
        await database.update_user(user_id, {"points": user_points})

    else:
        exercises_ids = state_data["exercises_ids"]
        exercises_ids.pop(0)
        exercises_ids.append(exercise_id)
        state_data["exercises_ids"] = exercises_ids

        exercises_done_text = f"Завдань виконано: <b>{exercises_quantity - len(exercises_ids)}/{exercises_quantity}</b>"
        caption = f"На жаль, ні 😥\nСпробуйте наступного разу\n\n{exercises_done_text}"

    await state.set_data(state_data)

    await message.answer_photo(
        photo=exercise_photo,
        caption=caption,
        reply_markup=UserFactory.correct_answer(exercise_educational_material, exercise_id)
    )


@router.callback_query(UserFactory.filter(F.action == "educational_material"))
async def exercise_options_call(
        call: CallbackQuery,
        callback_data: UserFactory,
        database: Database,
):
    await call.answer()

    exercise_id = int(callback_data.value)
    exercise = await database.get_exercise(exercise_id)
    educational_material = exercise.educational_material

    await call.message.edit_caption(caption=educational_material)
    await call.message.edit_reply_markup(reply_markup=UserFactory.educational_material())


@router.callback_query(NMTStates.type_answer)
async def ignore(call: CallbackQuery):
    await call.answer()

"""
@router.message(NMTStates.proceed_test)
@router.message(NMTStates.select_test)
@router.message(NMTStates.select_subject)
async def ignore_message(message: Message):
    await message.delete()


@router.message(NMTStates.type_answer)
@router.message(NMTStates.proceed_test)
@router.message(NMTStates.select_test)
@router.message(NMTStates.select_subject)
async def ignore_call(call: CallbackQuery):
    await call.answer()
"""
