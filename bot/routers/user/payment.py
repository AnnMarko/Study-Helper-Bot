from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from asyncio import sleep
import datetime

from app.database import Database
from app.configuration import Configuration
from bot.core.filters import check_user_subscription
from bot.core.keyboards import UserFactory


router = Router()


PRICE_1WEEK = LabeledPrice(label="Підписка на 1 тиждень", amount=1*100)  # 50*100)
URL_1WEEK = "https://i.pinimg.com/736x/1c/76/00/1c760058640ab0237717da70f8c4fb5f.jpg"
PRICE_1MONTH = LabeledPrice(label="Підписка на 1 місяць", amount=2*100)  # 150*100)
URL_1MONTH = "https://i.pinimg.com/736x/0d/d1/6c/0dd16c081b904df9921ba700593b2dad.jpg"
PRICE_3MONTHS = LabeledPrice(label="Підписка на 3 місяці", amount=3*100)  # 400*100)
URL_3MONTHS = "https://i.pinimg.com/736x/0b/c6/fd/0bc6fd45e29d9ca28de67932565ccab6.jpg"


@router.callback_query(UserFactory.filter(F.action == 'payments'))
async def payments(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    user_id = call.from_user.id
    subscription = await check_user_subscription(user_id, database)
    user = await database.get_user(user_id)

    text = (
        '<b>Меню платежів 💸</b>\n'
        '\n'
        'Статус підписки:\t'
           ) + (
        f'Активована ✅\n<i>до {user.payment_until.date() if user.payment_until else "..."}</i>'
        if subscription == True else 'Неактивована ❌\n'
    )

    await call.message.edit_text(text=text, reply_markup=UserFactory.payments_menu())


@router.callback_query(UserFactory.filter(F.action == 'select_payment'))
async def select_payment(
        call: CallbackQuery,
        callback_data: UserFactory,
        state: FSMContext,
        database: Database
):
    await call.answer()

    if callback_data.value == 'none':
        await call.message.edit_text(text="Оберіть план підписки 💳", reply_markup=UserFactory.select_payment())
        return

    await call.message.delete()
    payments_token = Configuration.payments_token

    if payments_token.split(':')[1] == 'TEST':
        await call.message.answer("Test!!!")

    match callback_data.value:
        case '0':
            await call.message.answer_invoice(title="Підписка на 1 тиждень",
                                              description="Активація підписки на 1 тиждень",
                                              provider_token=payments_token,
                                              currency="eur",
                                              photo_url=URL_1WEEK,
                                              photo_width=416,
                                              photo_height=234,
                                              photo_size=416,
                                              is_flexible=False,
                                              prices=[PRICE_1WEEK],
                                              start_parameter="one-week-subscription",
                                              payload="test-invoice-payload"
                                              )
        case '1':
            await call.message.answer_invoice(title="Підписка на 1 місяць",
                                              description="Активація підписки на 1 місяць",
                                              provider_token=payments_token,
                                              currency="uah",
                                              photo_url=URL_1MONTH,
                                              photo_width=416,
                                              photo_height=234,
                                              photo_size=416,
                                              is_flexible=False,
                                              prices=[PRICE_1MONTH],
                                              start_parameter="one-month-subscription",
                                              payload="test-invoice-payload"
                                              )
        case '2':
            await call.message.answer_invoice(title="Підписка на 3 місяці",
                                              description="Активація підписки на 3 місяці",
                                              provider_token=payments_token,
                                              currency="uah",
                                              photo_url=URL_3MONTHS,
                                              photo_width=416,
                                              photo_height=234,
                                              photo_size=416,
                                              is_flexible=False,
                                              prices=[PRICE_3MONTHS],
                                              start_parameter="three-months-subscription",
                                              payload="test-invoice-payload"
                                              )


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, database: Database):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await message.answer(
        f"Оплата на суму {message.successful_payment.total_amount // 100} "
        f"{message.successful_payment.currency} пройшла успішно!!!"
    )

    user_id = message.from_user.id
    print(user_id)
    print(message.successful_payment.order_info)
    print(message.successful_payment.model_fields)
    print(datetime.datetime.now())

    await database.update_user(user_id, {"payment_datetime": datetime.datetime.now()})
