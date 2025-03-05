from aiogram import Router

from . import (
    main,
    other,
    add_test,
    select_edit,
    edit_test,
    delete_test,
    select_edit_exercise,
    edit_exercise,
    add_exercise,
    message_to_all,
    promocode,
)


router = Router()


router.include_routers(
    main.router,
    other.router,
    message_to_all.router,
    add_test.router,
    select_edit.router,
    edit_test.router,
    delete_test.router,
    select_edit_exercise.router,
    edit_exercise.router,
    add_exercise.router,
    promocode.router,
)
