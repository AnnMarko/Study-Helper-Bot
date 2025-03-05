from aiogram.fsm.state import State, StatesGroup


class EditExerciseStates(StatesGroup):
    test_id = State()
    edit_exercise = State()
    delete_confirmation = State()
