from aiogram.fsm.state import State, StatesGroup


class GPTStates(StatesGroup):
    gpt_request = State()
    process = State()
