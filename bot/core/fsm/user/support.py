from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    type_message = State()
