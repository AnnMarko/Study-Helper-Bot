from __future__ import annotations

from typing import cast

from sqlalchemy import delete as sql_delete
from sqlalchemy import select as sql_select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ExerciseModel


async def get(session: AsyncSession, exercise_id: int) -> ExerciseModel | None:
    return await session.get(
        ExerciseModel, exercise_id
    )


async def create(
        session: AsyncSession,
        test_id: int,
        number: int,
        photo_id: str,
        exercise_type: int,
        options: int | None,
        correct_answer_list: list[int] | None,
        correct_answer_str: str | None,
        correct_answer_int: int | None,
        educational_material: str | None,
) -> ExerciseModel:
    new_user = ExerciseModel(
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
    session.add(new_user)
    await session.commit()
    return new_user


async def update(
        session: AsyncSession,
        exercise_id: int,
        update_context: dict,
) -> None:
    await session.execute(
        sql_update(ExerciseModel).where(ExerciseModel.exercise_id == exercise_id).values(
            update_context
        )
    )
    await session.commit()


async def delete(session: AsyncSession, exercise_id: int) -> None:
    await session.execute(
        sql_delete(ExerciseModel).where(ExerciseModel.exercise_id == exercise_id)
    )
    await session.commit()


async def get_all(session: AsyncSession,) -> list[ExerciseModel]:
    return cast(list[ExerciseModel], (
        await session.scalars(sql_select(ExerciseModel))
    ).all())


async def get_all_by_test(session: AsyncSession, test_id: int) -> list[ExerciseModel]:
    return cast(list[ExerciseModel], (
        await session.scalars(
            sql_select(ExerciseModel).where((ExerciseModel.test_id == test_id)).order_by(ExerciseModel.number)
        )
    ).all())


async def get_by_number_in_test(session: AsyncSession, test_id: int, exercise_number: int) -> ExerciseModel:
    return (
        cast(list[ExerciseModel], (
            await session.scalars(
                sql_select(ExerciseModel).where(ExerciseModel.test_id == test_id)
                .where(ExerciseModel.number == exercise_number)
            )
        ).all())
    )[0]
