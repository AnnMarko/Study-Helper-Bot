import g4f
from g4f.errors import RateLimitError

import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from asyncio import sleep


from app.database import Database
from bot.core.filters import IsPremium, is_premium, check_user_subscription
from bot.core.keyboards import UserFactory
from bot.core.fsm import GPTStates
from .main import main_menu_c


router = Router()


async def get_response_to_photo(prompt: str, path: str):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            image=open(path, "rb"),
        )
        result = ""
        for message in response:
            result += message
        return result
    except RuntimeError:
        return 0
    except ExceptionGroup:
        return 0


async def get_response(prompt: str):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        result = ""
        for message in response:
            result += message
        return result
    except RateLimitError:
        return 0


async def premium_suggest(message, state):
    await state.clear()
    text = (
        '<b>Схоже, Ви використали пробні спроби, але це не біда!</b>\n\nПридбайте дуже дешево повний доступ, '
        'щоб проходити безліч тестів та отримувати відповіді на завдання\nОберіть термін дії Premium підписки'
    )

    await message.answer(
        text=text,
        reply_markup=UserFactory.select_payment()
    )


async def select_language(message, state, database, free_gpt_requests=None):
    await state.set_state(GPTStates.gpt_request)

    data = database._response_languages
    selected = [0]

    text = "Оберіть мову відповіді та надішліть завдання 🌐"

    if free_gpt_requests is not None:
        if free_gpt_requests == 0:
            await premium_suggest(message, state)
            return
        text += f"\n\n<i>Залишилось пробних запитів: <b>{free_gpt_requests}</b></i>"

    try:
        await message.edit_text(
            text=text,
            reply_markup=UserFactory.response_language(data, selected)
        )
    except TelegramBadRequest:
        message = await message.answer(
            text=text,
            reply_markup=UserFactory.response_language(data, selected)
        )
    finally:
        await state.set_data({"language": 0, "message": message})


@router.callback_query(UserFactory.filter(F.action == 'get_response_gpt'), IsPremium())
async def get_response_gpt_c(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database,
):
    await call.answer()

    if callback_data.value == 'none':
        await select_language(call.message, state, database)
        return

    match callback_data.value:
        case '0':
            lang = 0
        case '1':
            lang = 1
        case '2':
            lang = 2
        case _:
            lang = 0

    await state.update_data({"language": lang})

    data = database._response_languages
    selected = [lang]

    await call.message.edit_reply_markup(reply_markup=UserFactory.response_language(data, selected))


@router.callback_query(UserFactory.filter(F.action == 'get_response_gpt'))
async def get_free_response_gpt_c(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    user_id = call.from_user.id

    result = await check_user_subscription(user_id, database)
    if result:
        await select_language(call.message, state, database)
        return

    user = await database.get_user(user_id)

    free_gpt_requests = user.free_gpt_requests
    if free_gpt_requests > 0:
        await select_language(call.message, state, database, free_gpt_requests)
        return

    await call.message.delete()
    await premium_suggest(call.message, state)


@router.message(F.photo, GPTStates.gpt_request)
async def get_response_to_photo_c(
        message: Message,
        state: FSMContext,
        database: Database,
):
    state_data = await state.get_data()
    lang = state_data["language"]
    old_message = state_data["message"]

    match lang:
        case 0:
            language = 'ukrainian'
        case 1:
            language = 'english'
        case _:
            language = 'as in the task'

    await old_message.delete_reply_markup()

    await message.answer(text="Завдання отримано! Оброблюю...")
    await state.set_state(GPTStates.process)

    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    caption = f"Caption to this photo: \"{message.caption}\"" if message.caption else ""

    task_path = f"C:/Users/annar/PycharmProjects/StubyHelpBot/temporary_files/task{str(user_id)}.jpg"
    answer_path = f"C:/Users/annar/PycharmProjects/StubyHelpBot/temporary_files/answer{str(user_id)}.html"

    prompt = (
        "You are a student, your task is on the photo. "
        f"{caption}\n"
        "Make the task and write your answer with an explanation. Write code for an html page using your answer.\n"
        f"-answer in language {language}\n-html page aesthetically pleasant for eyes\n"
        f"-make sure that html page will display the answer properly both on phone and computer\n"
        f"\n-add support for ios display\n-the whole detailed answer must be in the code"
    )
    print(prompt)

    await message.bot.download(file_id, destination=task_path)

    result = await get_response_to_photo(prompt, task_path)
    if not result:
        await message.answer(text="Упс.. Якась поламка😓 Спробуйте надіслати фото ще раз")
        await sleep(0.8)
        await select_language(message, state, database)
        return

    print("result:", result)

    start = result.rfind("```html") + 8
    if start == 7:
        start = result.rfind("<code>") + 7
        if start == 6:
            await message.answer(text="Упс.. Якась поламка😓 Спробуйте ще раз")
            await sleep(0.8)
            await select_language(message, state, database)
            return
        else:
            end = result.rfind("</code>")
    else:
        end = result.rfind("```")

    if end == start - 8:
        for i in range(4):
            if end != start - 8:
                break
            prompt = (
                "You are a student, who studies at school or university and you have a task. Task is on photo. "
                f"You have to write answer in html code. The beginning of the answer: \n'{result}'\nFinish the code and"
                " send me the whole code."
            )
            result = await get_response_to_photo(prompt, task_path)
            if not result:
                await message.answer(text="Упс.. Якась поламка😓 Спробуйте надіслати фото ще раз")
                await sleep(0.8)
                await select_language(message, state, database)
                return
            print("result again:", result)

            start = result.rfind("```html") + 8
            end = result.rfind("```")

    if end == start - 8:
        os.remove(task_path)
        await message.answer(text="Упс.. Якась поламка😓 Спробуйте ще раз")
        await sleep(0.8)
        await select_language(message, state, database)
        return

    html_text = result[start:end]
    print("html:", html_text)

    with open(answer_path, "w", encoding='utf-8') as file:
        file.write(html_text)

    document = FSInputFile(answer_path)
    await message.answer_document(document=document)

    os.remove(task_path)
    os.remove(answer_path)

    user = await database.get_user(user_id)

    if not await is_premium(user_id, database):
        free_gpt_requests = user.free_gpt_requests - 1
        await database.update_user(user_id, {"free_gpt_requests": free_gpt_requests})
        await select_language(message, state, database, free_gpt_requests)
        return

    await select_language(message, state, database)


@router.message(GPTStates.gpt_request)
async def get_response_c(
        message: Message,
        state: FSMContext,
        database: Database,
):
    state_data = await state.get_data()
    lang = state_data["language"]
    old_message = state_data["message"]

    match lang:
        case 0:
            language = 'ukrainian'
        case 1:
            language = 'english'
        case _:
            language = 'as in the task'

    await old_message.delete_reply_markup()

    await message.answer(text="Завдання отримано! Оброблюю...")
    await state.set_state(GPTStates.process)

    user_id = message.from_user.id

    task = message.text
    answer_path = f"C:/Users/annar/PycharmProjects/StubyHelpBot/temporary_files/answer{str(user_id)}.html"

    prompt = (
        f"You are a student, your task is \"{task}\". "
        f"Make the task and write your answer with an explanation. Write code for an html page using your answer.\n"
        f"-answer in language {language}\n-html page aesthetically pleasant for eyes\n"
        "-make sure that html page will display the answer properly both on phone and computer\n"
        "\n-add support for ios display\n-the whole detailed answer must be in the code"
    )

    result = await get_response(prompt)
    print("result:", result)

    if not result:
        await message.answer(text="Упс.. Якась поламка😓 Спробуйте надіслати завдання ще раз")
        await sleep(0.8)
        await select_language(message, state, database)
        return

    start = result.rfind("```html") + 8
    end = result.rfind("```")

    if end == start - 8:
        for i in range(3):
            if end != start - 8:
                break
            prompt = (
                f"You are a student, who studies at school or university and you have a task. Task is \"{task}\". "
                f"You have to write answer in html code. The beginning of the answer: \n'{result}'\nFinish the code and"
                " send me the whole code."
            )
            result = await get_response(prompt)
            print("result again:", result)

            start = result.rfind("```html") + 8
            end = result.rfind("```")

    if end == start - 8:
        await message.answer(text="Упс.. Якась поламка😓 Спробуйте ще раз")
        await select_language(message, state, database)
        return

    html_text = result[start:end]
    print("html:", html_text)

    with open(answer_path, "w", encoding='utf-8') as file:
        file.write(html_text)

    document = FSInputFile(answer_path)
    await message.answer_document(document=document)

    os.remove(answer_path)

    user = await database.get_user(user_id)

    if not await is_premium(user_id, database):
        free_gpt_requests = user.free_gpt_requests - 1
        await database.update_user(user_id, {"free_gpt_requests": free_gpt_requests})
        await select_language(message, state, database, free_gpt_requests)
        return

    await select_language(message, state, database)


@router.callback_query(UserFactory.filter(F.action == 'cancel_gpt'))
async def cancel(call: CallbackQuery, state: FSMContext):
    await main_menu_c(call, state)


@router.message(GPTStates.gpt_request)
@router.message(GPTStates.process)
async def ignore_message(message: Message):
    await message.delete()


@router.callback_query(GPTStates.gpt_request)
@router.callback_query(GPTStates.process)
async def ignore_call(call: CallbackQuery):
    await call.answer()
