from aiogram.fsm.state import State, StatesGroup


class PromocodeStates(StatesGroup):
    generate_promocode = State()
