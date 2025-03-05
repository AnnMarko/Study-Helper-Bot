from __future__ import annotations

from typing import cast

from sqlalchemy import delete as sql_delete
from sqlalchemy import select as sql_select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import TestModel


async def get(session: AsyncSession, test_id: int) -> TestModel | None:
    return await session.get(
        TestModel, test_id
    )


async def create(
        session: AsyncSession,
        title: str | None,
        subject: int,
) -> TestModel:
    new_test = TestModel(
        title=title,
        subject=subject,
    )
    session.add(new_test)
    await session.commit()
    return new_test


async def update(
        session: AsyncSession,
        test_id: int,
        update_context: dict,
) -> None:
    await session.execute(
        sql_update(TestModel).where(TestModel.test_id == test_id).values(
            update_context
        )
    )
    await session.commit()


async def delete(session: AsyncSession, test_id: int) -> None:
    await session.execute(
        sql_delete(TestModel).where(TestModel.test_id == test_id)
    )
    await session.commit()


async def get_all(session: AsyncSession,) -> list[TestModel]:
    return cast(list[TestModel], (
        await session.scalars(sql_select(TestModel))
    ).all())


async def get_all_by_subject(session: AsyncSession, subject: int) -> list[TestModel]:
    return cast(list[TestModel], (
        await session.scalars(
            sql_select(TestModel).where((TestModel.subject == subject))
        )
    ).all())


async def get_all_available_by_subject(session: AsyncSession, subject: int) -> list[TestModel]:
    return cast(list[TestModel], (
        await session.scalars(
            sql_select(TestModel).where(TestModel.subject == subject)
            .where(TestModel.is_available == True)
        )
    ).all())
