from asyncio import sleep

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm import AddExerciseStates
from app.database import Database

from .select_edit_exercise import select_edit_exercise


router = Router()


async def add_exercise_text(
        database: Database,
        state_data
):
    number = state_data["number"] if "number" in state_data else None
    exercise_type = state_data["exercise_type"] if "exercise_type" in state_data else None
    options = state_data["options"] if "options" in state_data else None
    correct_answer = state_data["correct_answer"] if "correct_answer" in state_data else None
    educational_material = state_data["educational_material"] if "educational_material" in state_data else None

    if options is not None:
        if exercise_type == 1:
            options_text = (database._options_3)[options]
        elif exercise_type == 2:
            options_text = (database._options_c)[options]
        else:
            options_text = (database._options)[options]
    else:
        options_text = '❓'

    if correct_answer is not None:
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
    else:
        answer_text = '❓'

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
        f"Навчальний матеріал: \t{educational_material if educational_material is not None else '❓'}"
    )
    return text


async def add_exercise(
        message,
        state: FSMContext,
        database: Database
):
    state_data = await state.get_data()

    correct_answer_is_available = False
    options_are_available = False
    is_finished = False

    if "exercise_type" in state_data:
        if state_data["exercise_type"] == 3:
            if (
                    "photo_id" in state_data and "exercise_type" in state_data
                    and "correct_answer" in state_data and "number" in state_data
            ):
                is_finished = True
        else:
            if (
                    "photo_id" in state_data and "exercise_type" in state_data and "options" in state_data
                    and "correct_answer" in state_data and "number" in state_data
            ):
                is_finished = True

    if "exercise_type" in state_data:
        options_are_available = True

        if state_data["exercise_type"] == 3:
            options_are_available = False
            correct_answer_is_available = True

        else:
            if "options" in state_data:
                correct_answer_is_available = True

    text = await add_exercise_text(database, state_data)

    try:
        photo_id = state_data["photo_id"]
        await message.answer_photo(
            caption=text,
            photo=photo_id,
            reply_markup=AdminFactory.add_exercise(correct_answer_is_available, options_are_available, is_finished)
        )
    except KeyError:
        await message.answer(
            text=text,
            reply_markup=AdminFactory.add_exercise(correct_answer_is_available, options_are_available, is_finished)
        )


@router.callback_query(AdminFactory.filter(F.action == "add_exercise"), IsAdmin())
async def add_exercise_start_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    number = state_data["number"]
    photo_id = state_data["photo_id"]
    exercise_type = state_data["exercise_type"]
    options = state_data["options"] if "options" in state_data else None
    correct_answer = state_data["correct_answer"]
    educational_material = state_data["educational_material"] if "educational_material" in state_data else None
    test_id = state_data["test_id"]

    exercise = await database.create_exercise(
        test_id=test_id,
        number=number,
        photo_id=photo_id,
        exercise_type=exercise_type,
        options=options,
        educational_material=educational_material,
    )

    if exercise_type == 0:
        await database.update_exercise(exercise.exercise_id, {"correct_answer_int": correct_answer})
    elif exercise_type in [1, 2]:
        await database.update_exercise(exercise.exercise_id, {"correct_answer_list": correct_answer})
    else:
        await database.update_exercise(exercise.exercise_id, {"correct_answer_str": correct_answer})

    test = await database.get_test(test_id)
    exercises_quantity = test.exercises_quantity + 1
    await database.update_test(test_id, {"exercises_quantity": exercises_quantity})

    message = await call.message.answer(text="Завдання додано успішно ❕")
    await sleep(1.7)
    await message.delete()

    await select_edit_exercise(call, database, state)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_start"), IsAdmin())
async def add_exercise_start_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()
    await call.message.delete()

    test_id = (await state.get_data())["test_id"]
    exercises = await database.get_all_exercises_by_test(test_id=test_id)

    number = 1
    if exercises:
        exercises_numbers = [exercise.number for exercise in exercises]
        exercises_numbers.sort()

        for i in range(len(exercises_numbers)):
            if number >= exercises_numbers[i]:
                number += 1

    await state.clear()
    await state.set_state(AddExerciseStates.start)
    await state.set_data({"test_id": test_id, "number": number})
    await add_exercise(call.message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_back"), IsAdmin())
async def add_exercise_back_c(
        call: CallbackQuery,
        state: FSMContext,
        database: Database
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()
    if "message" in state_data:
        del state_data["message"]

    if "answer_dict" in state_data:
        del state_data["answer_dict"]

    await state.set_state(AddExerciseStates.start)
    await add_exercise(call.message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_number"), IsAdmin())
async def add_exercise_number_c(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    await state.set_state(AddExerciseStates.number)

    await call.message.delete()
    message = await call.message.answer(text="Введіть новий номер ✍️", reply_markup=AdminFactory.add_exercise_cancel())
    await state.update_data({"message": message})


@router.message(AddExerciseStates.number, IsAdmin())
async def enter_number(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()

    number = message.text
    state_data = await state.get_data()
    old_message = state_data.pop("message")

    if number.isdigit():
        number = int(number)
        if number > 90:
            await old_message.edit_text(text="Занадто великий номер завдання ❗️", reply_markup=None)
            await sleep(1.7)
            await old_message.edit_text(text="Введіть новий номер ✍️", reply_markup=AdminFactory.add_exercise_cancel())
            return

        state_data["number"] = number
        await state.set_data(state_data)
        await state.set_state(AddExerciseStates.start)

        await add_exercise(old_message, state, database)
        return

    await old_message.edit_text(text="Номер повинен бути числом ❗️", reply_markup=None)
    await sleep(1.7)
    await old_message.edit_text(text="Введіть новий номер ✍️", reply_markup=AdminFactory.add_exercise_cancel())


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_photo"), IsAdmin())
async def add_exercise_photo_c(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    await state.set_state(AddExerciseStates.photo_id)

    await call.message.delete()
    message = await call.message.answer(text="Надішліть фото 📷", reply_markup=AdminFactory.add_exercise_cancel())
    await state.update_data({"message": message})


@router.message(AddExerciseStates.photo_id, IsAdmin())
async def send_photo(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()
    state_data = await state.get_data()
    old_message = state_data.pop("message")

    try:
        photo_id = message.photo[-1].file_id
        state_data["photo_id"] = photo_id
        await state.set_data(state_data)
        await state.set_state(AddExerciseStates.start)

        await old_message.delete()
        await add_exercise(old_message, state, database)
    except TypeError:
        await old_message.edit_text(text="Потрібно надіслати фото ❗️", reply_markup=None)
        await sleep(1.7)
        await old_message.edit_text(text="Надішліть фото 📷", reply_markup=AdminFactory.add_exercise_cancel())


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_educational_material"), IsAdmin())
async def add_exercise_educational_material_c(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    await state.set_state(AddExerciseStates.educational_material)

    await call.message.delete()
    message = await call.message.answer(
        text="Введіть навчальний матеріал 📖",
        reply_markup=AdminFactory.add_exercise_cancel()
    )
    await state.update_data({"message": message})


@router.message(AddExerciseStates.educational_material, IsAdmin())
async def enter_educational_material(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()

    state_data = await state.get_data()
    old_message = state_data.pop("message")
    educational_material = message.text
    state_data["educational_material"] = educational_material
    await state.set_data(state_data)
    await state.set_state(AddExerciseStates.start)

    await old_message.delete()
    await add_exercise(old_message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_type"), IsAdmin())
async def add_exercise_type_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if callback_data.value == 'none':
        await state.set_state(AddExerciseStates.exercise_type)

        selected = [state_data["exercise_type"]] if "exercise_type" in state_data else []
        data = database._types

        await call.message.answer(
            text="Оберіть тип завдання ⁉️",
            reply_markup=AdminFactory.select_exercise_type(data, selected)
        )
        return

    state_data["exercise_type"] = int(callback_data.value)

    if "options" in state_data:
        del state_data["options"]
    if "correct_answer" in state_data:
        del state_data["correct_answer"]
    if "answer_dict" in state_data:
        del state_data["answer_dict"]
    if "answer_list" in state_data:
        del state_data["answer_list"]

    await state.set_state(AddExerciseStates.start)
    await state.set_data(state_data)

    await add_exercise(call.message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_options"), IsAdmin())
async def add_exercise_options_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if callback_data.value == 'none':
        await state.set_state(AddExerciseStates.options)

        selected = [state_data["options"]] if "options" in state_data else []
        if state_data["exercise_type"] == 0:
            data = database._options
        elif state_data["exercise_type"] == 1:
            data = database._options_3
        else:
            data = database._options_c

        await call.message.answer(
            text="Оберіть кількість варіантів відповіді 📝",
            reply_markup=AdminFactory.select_exercise_options(data, selected)
        )
        return

    state_data["options"] = int(callback_data.value)

    if "correct_answer" in state_data:
        del state_data["correct_answer"]
    if "answer_dict" in state_data:
        del state_data["answer_dict"]
    if "answer_list" in state_data:
        del state_data["answer_list"]

    await state.set_data(state_data)
    await state.set_state(AddExerciseStates.start)

    await add_exercise(call.message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_answer"), IsAdmin())
async def add_exercise_answer_call(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if callback_data.value == 'none':

        await state.set_state(AddExerciseStates.correct_answer)
        exercise_type = state_data["exercise_type"]

        if exercise_type == 0:
            if state_data["options"] == 0:
                data = {k: v for k, v in database._options_letters.items() if k != 4}
            else:
                data = database._options_letters

        elif exercise_type == 1:
            if state_data["options"] == 0:
                data = {k: v for k, v in database._options_numbers.items() if k <= 4}
            elif state_data["options"] == 1:
                data = {k: v for k, v in database._options_numbers.items() if k <= 6}
            else:
                print("error add_exercise answer")
                data = database._options_numbers

            selected = []
            if "correct_answer" in state_data:
                selected = state_data["correct_answer"]

            is_done = len(selected) == 3

            state_data["answer_list"] = selected
            await state.set_data(state_data)

            await call.message.answer(
                text="Оберіть правильні варіанти відповіді ✔️",
                reply_markup=AdminFactory.select_exercise_answer_3(data, selected, is_done)
            )
            return

        elif exercise_type == 2:

            numbers_len, letters_len = (database._options_c[state_data["options"]]).split(":")
            numbers_len = int(numbers_len)
            letters_len = int(letters_len)

            selected = {}
            if "answer_dict" in state_data:
                selected = [state_data["answer_dict"]]
            else:
                if "correct_answer" in state_data:
                    for i in range(numbers_len):
                        selected[i] = state_data["correct_answer"][i]

            is_done = len(selected) == numbers_len

            letters = {k: v for k, v in database._options_letters.items() if k < letters_len}

            numbers = {k: v for k, v in database._options_numbers.items() if k < numbers_len}

            state_data["answer_dict"] = selected
            await state.set_data(state_data)

            await call.message.answer(
                text="Оберіть правильні варіанти відповіді ✔️",
                reply_markup=AdminFactory.select_exercise_answer_c(letters, numbers, selected, is_done)
            )
            return

        else:
            await state.set_state(AddExerciseStates.enter_answer)
            text = (
                "Надішліть правильну відповідь\n\n<i>Приклад правильного запису:\n3,4    2/3\n"
                "Приклад неправильного запису:\n3.4    2 / 3</i>"
            )
            message = await call.message.answer(
                text=text,
                reply_markup=AdminFactory.add_exercise_cancel()
            )
            await state.update_data({"message": message})
            return

        selected = [state_data["correct_answer"]] if "correct_answer" in state_data else []

        await call.message.answer(
            text="Оберіть правильний варіант відповіді ✔️",
            reply_markup=AdminFactory.select_exercise_answer(data, selected)
        )
        return

    state_data["correct_answer"] = int(callback_data.value)

    await state.set_data(state_data)
    await state.set_state(AddExerciseStates.start)

    await add_exercise(call.message, state, database)


@router.message(AddExerciseStates.enter_answer, IsAdmin())
async def enter_answer(
        message: Message,
        state: FSMContext,
        database: Database,
):
    await message.delete()

    state_data = await state.get_data()
    old_message = state_data.pop("message")
    correct_answer = message.text
    state_data["correct_answer"] = correct_answer
    await state.set_data(state_data)
    await state.set_state(AddExerciseStates.start)

    await old_message.delete()
    await add_exercise(old_message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_answer_c"), IsAdmin())
async def add_exercise_answer_c(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if callback_data.value != 'none':
        numbers_len, letters_len = (database._options_c[state_data["options"]]).split(":")
        numbers_len = int(numbers_len)
        letters_len = int(letters_len)

        selected = {}
        if "answer_dict" in state_data:
            selected = state_data["answer_dict"]
        else:
            if "correct_answer" in state_data:
                for i in range(numbers_len):
                    selected[i] = state_data["correct_answer"][i]

        new_number, new_letter = callback_data.value.split('-')
        new_number = int(new_number)
        new_letter = int(new_letter)

        selected[new_number] = new_letter

        is_done = len(selected) == numbers_len

        letters = {k: v for k, v in database._options_letters.items() if k <= letters_len - 1}

        numbers = {k: v for k, v in database._options_numbers.items() if k <= numbers_len - 1}

        state_data["answer_dict"] = selected
        await state.set_data(state_data)

        await call.message.answer(
            text="Оберіть правильні варіанти відповіді ✔️",
            reply_markup=AdminFactory.select_exercise_answer_c(letters, numbers, selected, is_done)
        )
        return

    answer_dict = state_data.pop("answer_dict")
    correct_answer = []
    for index, value in answer_dict.items():
        correct_answer.append(value)

    state_data["correct_answer"] = correct_answer

    await state.set_state(AddExerciseStates.start)
    await state.set_data(state_data)

    await add_exercise(call.message, state, database)


@router.callback_query(AdminFactory.filter(F.action == "add_exercise_answer_3"), IsAdmin())
async def add_exercise_answer_3(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()

    if callback_data.value != 'none':
        if state_data["options"] == 0:
            numbers = {k: v for k, v in database._options_numbers.items() if k <= 4}
        elif state_data["options"] == 1:
            numbers = {k: v for k, v in database._options_numbers.items() if k <= 6}
        else:
            print("error add_exercise answer")
            numbers = database._options_numbers

        selected = []
        if "answer_list" in state_data:
            selected = state_data["answer_list"]
        else:
            if "correct_answer" in state_data:
                selected = state_data["correct_answer"]

        new_number = int(callback_data.value)

        selected.append(new_number)
        while len(selected) > 3:
            selected.pop(0)

        is_done = len(selected) == 3

        state_data["answer_list"] = selected
        await state.set_data(state_data)

        await call.message.answer(
            text="Оберіть правильні варіанти відповіді ✔️",
            reply_markup=AdminFactory.select_exercise_answer_3(numbers, selected, is_done)
        )
        return

    correct_answer = state_data.pop("answer_list")

    state_data["correct_answer"] = correct_answer

    await state.set_state(AddExerciseStates.start)
    await state.set_data(state_data)

    await add_exercise(call.message, state, database)


@router.callback_query(AddExerciseStates.number, IsAdmin())
@router.callback_query(AddExerciseStates.photo_id, IsAdmin())
@router.callback_query(AddExerciseStates.educational_material, IsAdmin())
@router.callback_query(AddExerciseStates.enter_answer, IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()

"""
@router.message(AddExerciseStates.start)
@router.message(AddExerciseStates.exercise_type)
@router.message(AddExerciseStates.options)
@router.message(AddExerciseStates.correct_answer)
async def ignore_message(message: Message):
    await message.delete()


@router.message(AddExerciseStates.start)
@router.message(AddExerciseStates.exercise_type)
@router.message(AddExerciseStates.options)
@router.message(AddExerciseStates.correct_answer)
@router.message(AddExerciseStates.photo_id)
@router.message(AddExerciseStates.number)
@router.message(AddExerciseStates.educational_material)
@router.message(AddExerciseStates.enter_answer)
async def ignore_call(call: CallbackQuery):
    await call.answer()
"""
