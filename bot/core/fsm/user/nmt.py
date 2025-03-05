from aiogram.fsm.state import State, StatesGroup


class NMTStates(StatesGroup):
    select_subject = State()
    select_test = State()
    proceed_test = State()
    type_answer = State()
