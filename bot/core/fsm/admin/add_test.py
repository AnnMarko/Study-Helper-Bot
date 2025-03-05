from aiogram.fsm.state import State, StatesGroup


class AddTestStates(StatesGroup):
    title = State()
    subject = State()
    confirmation = State()

