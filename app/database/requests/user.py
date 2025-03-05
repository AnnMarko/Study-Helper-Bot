from __future__ import annotations

from typing import cast

from sqlalchemy import delete as sql_delete
from sqlalchemy import select as sql_select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserModel


async def get(session: AsyncSession, user_id: int) -> UserModel | None:
    return await session.get(
        UserModel, user_id
    )


async def create(
        session: AsyncSession,
        user_id: int,
        full_name: str,

) -> UserModel:
    new_user = UserModel(
        user_id=user_id,
        full_name=full_name,
    )
    session.add(new_user)
    await session.commit()
    return new_user


async def update(
        session: AsyncSession,
        user_id: int,
        update_context: dict,
) -> None:
    await session.execute(
        sql_update(UserModel).where(UserModel.user_id == user_id).values(
            update_context
        )
    )
    await session.commit()


async def delete(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        sql_delete(UserModel).where(UserModel.user_id == user_id)
    )
    await session.commit()


async def get_all(session: AsyncSession,) -> list[UserModel]:
    return cast(list[UserModel], (
        await session.scalars(sql_select(UserModel))
    ).all())


async def get_50_best(session: AsyncSession,) -> list[UserModel]:
    return cast(list[UserModel], (
        await session.scalars(sql_select(UserModel).where(UserModel.nickname != None).order_by(UserModel.points.desc()))
    ).all()[:50])
