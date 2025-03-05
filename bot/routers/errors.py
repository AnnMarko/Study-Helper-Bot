from aiogram.types import ErrorEvent, Message
from aiogram import Router, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNetworkError, TelegramForbiddenError, TelegramBadRequest


router = Router()


@router.error(ExceptionTypeFilter(TelegramNetworkError), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Упс.. Щось пішло не так 😓")
    print("TelegramNetworkError")


@router.error(ExceptionTypeFilter(TelegramForbiddenError), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent):
    print("TelegramForbiddenError")
"""

@router.error(ExceptionTypeFilter(TelegramBadRequest), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent):
    print("TelegramBadRequest")


@router.error()
async def handle_my_custom_exception(event: ErrorEvent):
    if type(event.exception) == KeyError or type(event.exception) == AttributeError:
        call = event.update.callback_query
        await call.answer()
        await call.message.delete()
        return
    print(event)
    print("CRITYCAL ERROR")
"""