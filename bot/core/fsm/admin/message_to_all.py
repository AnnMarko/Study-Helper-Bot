from aiogram.fsm.state import State, StatesGroup


class MessageToAllStates(StatesGroup):
    type_message = State()
    send_confirmation = State()
