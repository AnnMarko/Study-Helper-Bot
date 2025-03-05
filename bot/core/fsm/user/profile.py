from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    enter_nickname = State()
