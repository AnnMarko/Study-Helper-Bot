from aiogram import Router

from . import (
    main,
    gpt,
    payment,
    start_nmt,
    proceed_nmt,
    other,
    support,
    profile,
    leaderboard,
    promocode,
)


router = Router()


router.include_routers(
    gpt.router,
    main.router,
    support.router,
    payment.router,
    start_nmt.router,
    proceed_nmt.router,
    profile.router,
    promocode.router,
    leaderboard.router,
    other.router,
)
