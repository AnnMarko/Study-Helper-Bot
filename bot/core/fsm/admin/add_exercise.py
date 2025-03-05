from aiogram.fsm.state import State, StatesGroup


class AddExerciseStates(StatesGroup):
    start = State()
    number = State()
    photo_id = State()
    exercise_type = State()
    options = State()
    correct_answer = State()
    enter_answer = State()
    educational_material = State()
