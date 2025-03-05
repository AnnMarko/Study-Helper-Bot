from aiogram import Router
from aiogram.types import Message


router = Router()


@router.message()
async def ignore_message(message: Message):
    await message.delete()
