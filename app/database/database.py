from typing import Optional

from aiogram.types import User
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    UserModel,
    TestModel,
    ExerciseModel,
    PromocodeModel,
)

from .requests import (
    user,
    test,
    exercise,
    promocode,
)

RESPONSE_LANGUAGES = {
    0: "Українська",
    1: "Англійська",
    2: "Як у завданні",
}

SUBJECTS = {
    0: "Українська мова",
    1: "Математика",
    2: "Історія України",
}

TYPES = {
    0: "Одна правильна відповідь",
    1: "Три правильні відповіді",
    2: "Відповідність",
    3: "Вписати відповідь самостійно",
}

OPTIONS = {
    0: "4",
    1: "5",
}

OPTIONS_3 = {
    0: "5",
    1: "7",
}

OPTIONS_C = {
    0: "4 : 4",
    1: "4 : 5",
    2: "3 : 5",
}

OPTIONS_LETTERS = {
    0: "А",
    1: "Б",
    2: "В",
    3: "Г",
    4: "Д",
}

OPTIONS_NUMBERS = {
    0: "1",
    1: "2",
    2: "3",
    3: "4",
    4: "5",
    5: "6",
    6: "7",
}


class Database:
    def __init__(self, session_db: AsyncSession) -> None:
        self.session_db = session_db

    _response_languages = RESPONSE_LANGUAGES
    _subjects = SUBJECTS
    _types = TYPES
    _options = OPTIONS
    _options_3 = OPTIONS_3
    _options_c = OPTIONS_C
    _options_letters = OPTIONS_LETTERS
    _options_numbers = OPTIONS_NUMBERS

    """ users DATABASE """
    async def get_user(self,  user_id: int) -> Optional[UserModel]:
        return await user.get(
            user_id=user_id,
            session=self.session_db
        )

    async def create_user(self, telegram_user: User) -> UserModel:
        return await user.create(
            session=self.session_db,
            user_id=telegram_user.id,
            full_name=telegram_user.full_name,
        )

    async def update_user(self, user_id: int, update_context: dict) -> None:
        await user.update(
            user_id=user_id,
            update_context=update_context,
            session=self.session_db
        )

    async def delete_user(self, user_id: int) -> None:
        await user.delete(
            user_id=user_id,
            session=self.session_db
        )

    async def get_all_users(self) -> list[UserModel]:
        return await user.get_all(
            session=self.session_db
        )

    async def get_50_best_users(self) -> list[UserModel]:
        return await user.get_50_best(
            session=self.session_db
        )

    """ tests DATABASE """
    async def get_test(self,  test_id: int) -> Optional[TestModel]:
        return await test.get(
            test_id=test_id,
            session=self.session_db
        )

    async def create_test(self, title: str | None, subject: int) -> TestModel:
        return await test.create(
            session=self.session_db,
            title=title,
            subject=subject,
        )

    async def update_test(self, test_id: int, update_context: dict) -> None:
        await test.update(
            test_id=test_id,
            update_context=update_context,
            session=self.session_db
        )

    async def delete_test(self, test_id: int) -> None:
        await test.delete(
            test_id=test_id,
            session=self.session_db
        )

    async def get_all_tests(self) -> list[TestModel]:
        return await test.get_all(
            session=self.session_db
        )

    async def get_all_tests_by_subject(self, subject: int) -> list[TestModel]:
        return await test.get_all_by_subject(
            session=self.session_db,
            subject=subject
        )

    async def get_all_available_tests_by_subject(self, subject: int) -> list[TestModel]:
        return await test.get_all_available_by_subject(
            session=self.session_db,
            subject=subject
        )

    """ exercises DATABASE """
    async def get_exercise(self,  exercise_id: int) -> Optional[ExerciseModel]:
        return await exercise.get(
            exercise_id=exercise_id,
            session=self.session_db
        )

    async def create_exercise(
            self,
            test_id: int,
            number: int,
            photo_id: str,
            exercise_type: int,
            options: int | None,
            correct_answer_list: list[int] | None = None,
            correct_answer_str: str | None = None,
            correct_answer_int: int | None = None,
            educational_material: str | None = None,
    ) -> ExerciseModel:
        return await exercise.create(
            session=self.session_db,
            test_id=test_id,
            number=number,
            photo_id=photo_id,
            exercise_type=exercise_type,
            options=options,
            correct_answer_list=correct_answer_list,
            correct_answer_str=correct_answer_str,
            correct_answer_int=correct_answer_int,
            educational_material=educational_material,
        )

    async def update_exercise(self, exercise_id: int, update_context: dict) -> None:
        await exercise.update(
            exercise_id=exercise_id,
            update_context=update_context,
            session=self.session_db
        )

    async def delete_exercise(self, exercise_id: int) -> None:
        await exercise.delete(
            exercise_id=exercise_id,
            session=self.session_db
        )

    async def get_all_exercises(self) -> list[ExerciseModel]:
        return await exercise.get_all(
            session=self.session_db
        )

    async def get_all_exercises_by_test(self, test_id: int) -> list[ExerciseModel]:
        return await exercise.get_all_by_test(
            session=self.session_db,
            test_id=test_id
        )

    async def get_exercise_by_number_in_test(self, test_id: int, exercise_number: int) -> ExerciseModel:
        return await exercise.get_by_number_in_test(
            session=self.session_db,
            test_id=test_id,
            exercise_number=exercise_number
        )

    """ promocodes DATABASE """
    async def get_promocode(self,  promocode_id: int) -> Optional[PromocodeModel]:
        return await promocode.get(
            promocode_id=promocode_id,
            session=self.session_db
        )

    async def create_promocode(
            self,
            code: str,
            durability_days: int = 3,
    ) -> PromocodeModel:
        return await promocode.create(
            session=self.session_db,
            code=code,
            durability_days=durability_days,
        )

    async def update_promocode(self, promocode_id: int, update_context: dict) -> None:
        await promocode.update(
            promocode_id=promocode_id,
            update_context=update_context,
            session=self.session_db
        )

    async def delete_promocode(self, promocode_id: int) -> None:
        await promocode.delete(
            promocode_id=promocode_id,
            session=self.session_db
        )

    async def get_all_promocodes(self) -> list[PromocodeModel]:
        return await promocode.get_all(
            session=self.session_db
        )

    async def get_promocode_by_code(self, code: str) -> PromocodeModel:
        return await promocode.get_by_code(
            session=self.session_db,
            code=code
        )
