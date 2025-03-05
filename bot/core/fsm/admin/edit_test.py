from aiogram.fsm.state import State, StatesGroup


class EditTestStates(StatesGroup):
    test_id = State()
    subject = State()
    select_edit = State()
    edit_test = State()
    edit_title = State()
    title_confirmation = State()
    delete_confirmation = State()
    select_edit_exercise = State()
