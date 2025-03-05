from aiogram.fsm.state import State, StatesGroup


class UsePromocodeStates(StatesGroup):
    enter_promocode = State()
