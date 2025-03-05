from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from asyncio import sleep

from app.database import Database
from bot.core.keyboards import UserFactory
from bot.core.fsm import UsePromocodeStates
from .main import send_main_menu

import datetime


router = Router()


@router.callback_query(UserFactory.filter(F.action == 'enter_promocode'))
async def enter_promocode(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    await state.set_state(UsePromocodeStates.enter_promocode)
    await state.set_data({"message": call.message})

    await call.message.edit_text(text="Введіть Ваш промокод ✍️", reply_markup=UserFactory.enter_promocode())


@router.message(UsePromocodeStates.enter_promocode)
async def support_forward(
        message: Message,
        state: FSMContext,
        database: Database,
):
    old_message = (await state.get_data())["message"]
    await old_message.delete()
    await message.delete()
    await state.clear()

    all_promocodes = await database.get_all_promocodes()
    codes = [promocode.code for promocode in all_promocodes]
    code = message.text
    if code in codes:
        promocode = await database.get_promocode_by_code(code)
        await database.delete_promocode(promocode.promocode_id)
        user_id = message.from_user.id
        user = await database.get_user(user_id)

        payment_until = user.payment_until
        if payment_until:
            payment_until = payment_until + datetime.timedelta(days=promocode.durability_days)
        else:
            payment_until = datetime.timedelta(days=promocode.durability_days) + datetime.datetime.now()

        data = {"payment_until": payment_until}

        if user.gpt_premium == False:
            data["gpt_premium"] = True

        await database.update_user(user_id, data)

        await message.answer(text=f"Чудово! Ваша підиска подовжена до {payment_until.date()} ✔️")
        await sleep(1.7)
    else:
        temporary_message = await message.answer(text="Такого промокоду не існує ❗️")
        await sleep(1.7)
        await temporary_message.delete()

    await send_main_menu(message)


@router.callback_query(UsePromocodeStates.enter_promocode)
async def ignore(call: CallbackQuery):
    await call.answer()
