from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.filters import IsAdmin
from bot.core.keyboards import AdminFactory
from bot.core.fsm.admin import PromocodeStates
from .main import admin

from app.database import Database

from asyncio import sleep
import random


router = Router()


@router.callback_query(AdminFactory.filter(F.action == 'generate_promocode'), IsAdmin())
async def generate_promocode(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()

    await state.set_state(PromocodeStates.generate_promocode)

    characters = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's',
        'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm'
    ]

    promocode = ''
    for i in range(8):
        promocode += random.choice(characters)

    await state.set_data({"promocode": promocode})

    await call.message.edit_text(
        text=f'Згенерований промокод:\n\n<b>{promocode}</b>\n\nБажаєте зберегти його?',
        reply_markup=AdminFactory.confirm_generate_promocode()
    )


@router.callback_query(
    AdminFactory.filter(F.action == 'confirm_generate_promocode'), PromocodeStates.generate_promocode, IsAdmin()
)
async def generate_promocode(
        call: CallbackQuery,
        callback_data: AdminFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    if callback_data.value == '0':
        await call.message.delete()
        await state.clear()
        await admin(call.message)
    elif callback_data.value == '1':
        promocode = (await state.get_data())["promocode"]
        await database.create_promocode(code=promocode)
        await call.message.edit_text(
            text='Промокод збережено ❕',
            reply_markup=None
        )
        await sleep(0.5)
        await call.message.answer(text=f'<b>{promocode}</b>')
        await state.clear()
        await sleep(1.7)
        await admin(call.message)


@router.callback_query(PromocodeStates.generate_promocode, IsAdmin())
async def ignore(call: CallbackQuery):
    await call.answer()
