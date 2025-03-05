import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine

from app.configuration import Configuration
from app.database import Base

from bot.core.middlewares import setup_middlewares
from bot.routers import setup_routers

import logging

logging.basicConfig(level=logging.INFO)


async def main():
    config = Configuration()
    # setup dispatcher and bot
    dispatcher = Dispatcher()

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode="html", link_preview_is_disabled=True))

    setup_middlewares(dispatcher=dispatcher)
    # setup routers
    setup_routers(dispatcher=dispatcher)

    engine = create_async_engine(config.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # start polling
    await dispatcher.start_polling(
        bot,
        session_pool=config.session_pool,
        config=config,
    )


if __name__ == "__main__":
    asyncio.run(main())
