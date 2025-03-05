from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from asyncio import sleep

from bot.core.keyboards import UserFactory
from bot.core.fsm import NMTStates
from bot.core.filters import is_premium, check_user_subscription
from app.database import Database

from .proceed_nmt import get_exercises


router = Router()


async def get_available_tests(user_id, database, state):
    subject = (await state.get_data())["subject"]
    tests = await database.get_all_available_tests_by_subject(subject)

    if not tests:
        return False

    tests_ids = [test.test_id for test in tests]
    tests_ids.sort()
    tests_ids.reverse()

    match subject:
        case 0:
            done_tests_ids = (await database.get_user(user_id)).ukr_tests_done
            done_exercises_ids = (await database.get_user(user_id)).ukr_exercises_done
        case 1:
            done_tests_ids = (await database.get_user(user_id)).math_tests_done
            done_exercises_ids = (await database.get_user(user_id)).math_exercises_done
        case 2:
            done_tests_ids = (await database.get_user(user_id)).hist_tests_done
            done_exercises_ids = (await database.get_user(user_id)).hist_exercises_done
        case _:
            done_tests_ids = []
            done_exercises_ids = []

    tests_ids_list = []

    for test_id in tests_ids:
        exercises = await database.get_all_exercises_by_test(test_id)
        exercises_ids = [exercise.exercise_id for exercise in exercises]
        if test_id not in done_tests_ids and set(done_exercises_ids) & set(exercises_ids):
            tests_ids_list.append(test_id)

    tests_ids = [test_id for test_id in tests_ids if test_id not in tests_ids_list]

    tests_ids_list += [test_id for test_id in tests_ids if test_id not in done_tests_ids]
    for test_id in tests_ids:
        if test_id in done_tests_ids:
            tests_ids_list.append(test_id)

    await state.update_data({"tests_ids": tests_ids_list, "done_tests_ids": done_tests_ids, "user_id": user_id})
    return True


async def select_test_nmt(message, database, state):
    state_data = await state.get_data()

    index = state_data["current_test_index"]
    tests_ids = state_data["tests_ids"]
    subject = state_data["subject"]

    test_id = tests_ids[index]
    done_tests_ids = state_data["done_tests_ids"]

    is_done = test_id in done_tests_ids

    test = await database.get_test(test_id)
    exercises_quantity = test.exercises_quantity
    title = test.title
    title_text = f"{title}\n" if title else ""

    exercises = await database.get_all_exercises_by_test(test_id)
    exercises_ids = [exercise.exercise_id for exercise in exercises]
    user_id = state_data["user_id"]
    user = await database.get_user(user_id)
    match subject:
        case 0:
            user_done_exercises = user.ukr_exercises_done
        case 1:
            user_done_exercises = user.math_exercises_done
        case 2:
            user_done_exercises = user.hist_exercises_done
        case _:
            user_done_exercises = []

    user_done_exercises_count = 0
    for exercise_id in exercises_ids:
        if exercise_id in user_done_exercises:
            user_done_exercises_count += 1

    exercises_quantity_text = (
        f"{exercises_quantity}" if test_id in done_tests_ids or user_done_exercises_count == 0 else
        f"{user_done_exercises_count}/{exercises_quantity}"
    )

    if test_id in done_tests_ids:
        status = "Завершено ✅"
    elif user_done_exercises_count > 0:
        status = "В процесі ⚠️"
    else:
        status = "Не завершено ❗️"

    await state.update_data({"current_test_id": test_id, "current_test_index": index})

    text = (f"<b>📃 Тести</b>\n"
            f"<i>{database._subjects[subject]}</i>\n"
            f"\n"
            f"{title_text}\n"
            f"\n"
            f"Завдань: {exercises_quantity_text}\n"
            f"<i>{status}</i>"
            )
    await message.edit_text(text=text, reply_markup=UserFactory.select_test_nmt(len(tests_ids), index, is_done))


async def select_subject_nmt(call, state):
    await state.set_state(NMTStates.select_subject)

    await call.message.edit_text(
        text="<b>Оберіть предмет</b> 📚\n\n<i>для проходження пробного тесту</i>",
        reply_markup=UserFactory.select_subject_nmt()
    )


@router.callback_query(UserFactory.filter(F.action == 'select_subject_nmt'))
async def select_subject_nmt_c(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
) -> None:
    await call.answer()

    if callback_data.value == 'none':
        await select_subject_nmt(call, state)
        return

    subject = callback_data.value

    await state.update_data({"subject": int(subject), "current_test_index": 0})

    result = await get_available_tests(call.from_user.id, database, state)

    if not result:
        await call.message.edit_text(text="На жаль, зараз немає доступних тестів")
        temporary_message = await call.message.answer(text="🤷")
        await sleep(1.7)
        await temporary_message.delete()
        await state.clear()
        await select_subject_nmt(call, state)
        return

    await state.set_state(NMTStates.select_test)
    await select_test_nmt(call.message, database, state)


@router.callback_query(UserFactory.filter(F.action == 'select_test_nmt'), NMTStates.select_test)
async def select_test_nmt_c(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
) -> None:
    await call.answer()

    async def available_for_taking(state_data_f, message, selected_again=False):
        test_id_f = state_data_f["current_test_id"]
        exercises_f = await database.get_all_exercises_by_test(test_id_f)
        exercises_ids_f = [exercise.exercise_id for exercise in exercises_f]
        user_id_f = state_data_f["user_id"]
        user_f = await database.get_user(user_id_f)

        subject = state_data["subject"]
        match subject:
            case 0:
                is_available = set(exercises_ids_f) & set(user_f.ukr_exercises_done)
            case 1:
                is_available = set(exercises_ids_f) & set(user_f.math_exercises_done)
            case 2:
                is_available = set(exercises_ids_f) & set(user_f.hist_exercises_done)
            case _:
                is_available = False

        if (
            selected_again or
                (
                    (
                        len(user_f.ukr_tests_done) >= 1 or
                        len(user_f.math_tests_done) >= 1 or
                        len(user_f.hist_tests_done) >= 1
                    ) and not is_available
                )
        ):
            result_f = await check_user_subscription(user_id_f, database)
            if result_f:
                return True
            await message.delete()
            text_f = (
                '<b>Схоже, Ви використали пробну спробу, але це не біда!</b>\n\nПридбайте дуже дешево повний доступ '
                'щоб проходити безліч тестів та отримувати відповіді на завдання'
            )
            await message.answer(
                text=text_f,
                reply_markup=UserFactory.select_payment()
            )
            return False

        return True

    state_data = await state.get_data()
    call_data = callback_data.value

    if call_data == "select":
        user_id = call.from_user.id

        if not await is_premium(user_id, database):
            result = await available_for_taking(state_data, call.message)
            if not result:
                return

        test_id = state_data["current_test_id"]
        await state.set_data({"test_id": test_id})
        await call.message.delete()
        await get_exercises(call, database, state)

    elif call_data == "select_again":
        user_id = call.from_user.id

        if not await is_premium(user_id, database):
            result = await available_for_taking(state_data, call.message, selected_again=True)
            if not result:
                return

        await call.message.edit_text(
            text="Ви бажаєте скласти цей тест ще раз?\n\n<i>Попередні результати будуть онульовані</i>",
            reply_markup=UserFactory.take_test_again_confirm()
        )

    elif call_data == "back":
        await state.clear()
        await select_subject_nmt(call, state)

    elif call_data == "go_back":
        index = state_data["current_test_index"] - 1
        await state.update_data({"current_test_index": index})
        await select_test_nmt(call.message, database, state)

    elif call_data == "go_back_five":
        index = state_data["current_test_index"] - 5
        if index < 0:
            index = 0
        await state.update_data({"current_test_index": index})
        await select_test_nmt(call.message, database, state)

    elif call_data == "go_forward":
        index = state_data["current_test_index"] + 1
        await state.update_data({"current_test_index": index})
        await select_test_nmt(call.message, database, state)

    elif call_data == "go_forward_five":
        index = state_data["current_test_index"] + 5
        tests_ids = state_data["tests_ids"]
        if index >= len(tests_ids):
            index = len(tests_ids) - 1
        await state.update_data({"current_test_index": index})
        await select_test_nmt(call.message, database, state)


@router.callback_query(UserFactory.filter(F.action == 'take_test_again'), NMTStates.select_test)
async def select_test_nmt_c(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
) -> None:
    await call.answer()

    state_data = await state.get_data()

    if callback_data.value == '0':
        await select_test_nmt(call.message, database, state)
        return

    test_id = state_data["current_test_id"]
    test = await database.get_test(test_id)
    user_id = call.from_user.id
    user = await database.get_user(user_id)
    exercises = await database.get_all_exercises_by_test(test_id)
    exercises_ids = [item.exercise_id for item in exercises]

    test_subject = test.subject

    match test_subject:
        case 0:
            old_tests_done = user.ukr_tests_done
            old_exercises_done = user.ukr_exercises_done
            tests_done = [item for item in old_tests_done if item != test_id]
            exercises_done = [item for item in old_exercises_done if item not in exercises_ids]
            await database.update_user(user_id, {"ukr_tests_done": tests_done, "ukr_exercises_done": exercises_done})
        case 1:
            old_tests_done = user.math_tests_done
            old_exercises_done = user.math_exercises_done
            tests_done = [item for item in old_tests_done if item != test_id]
            exercises_done = [item for item in old_exercises_done if item not in exercises_ids]
            await database.update_user(user_id, {"math_tests_done": tests_done, "math_exercises_done": exercises_done})
        case _:
            old_tests_done = user.hist_tests_done
            old_exercises_done = user.hist_exercises_done
            tests_done = [item for item in old_tests_done if item != test_id]
            exercises_done = [item for item in old_exercises_done if item not in exercises_ids]
            await database.update_user(user_id, {"hist_tests_done": tests_done, "hist_exercises_done": exercises_done})

    """
    remove_points = (old_exercises_done - exercises_done) * 5
    user_points = user.points - remove_points
    await database.update_user(user_id, {"points": user_points})
    """

    await state.set_data({"test_id": test_id})
    await call.message.delete()
    await get_exercises(call, database, state)
