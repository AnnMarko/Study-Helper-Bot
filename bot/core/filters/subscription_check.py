from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter

from app.configuration import Configuration
from app.database import Database

import datetime


async def check_user_subscription(user_id: int, database: Database):
    user = await database.get_user(user_id)
    if user.payment_until:
        if datetime.datetime.now(user.payment_until.tzinfo) > user.payment_until: # and user_id not in Configuration.admins:
            data = {"payment_until": None, "payment_datetime": None}
            if user.gpt_premium == True:
                data["gpt_premium"] = False
            await database.update_user(user_id, data)
        else:
            if user.gpt_premium == False:
                await database.update_user(user_id, {"gpt_premium": True})
    else:
        """
        if user_id not in Configuration.admins:
            if user.gpt_premium == True:
                await database.update_user(user_id, {"gpt_premium": False})
        else:
            if user.gpt_premium == False:
                await database.update_user(user_id, {"gpt_premium": True})
        """
        if user.gpt_premium == True:
            await database.update_user(user_id, {"gpt_premium": False})

    return user.gpt_premium
