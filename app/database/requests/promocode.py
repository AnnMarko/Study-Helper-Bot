from __future__ import annotations

from typing import cast

from sqlalchemy import delete as sql_delete
from sqlalchemy import select as sql_select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PromocodeModel


async def get(session: AsyncSession, promocode_id: int) -> PromocodeModel | None:
    return await session.get(
        PromocodeModel, promocode_id
    )


async def create(
        session: AsyncSession,
        code: str,
        durability_days: int,
) -> PromocodeModel:
    new_promocode = PromocodeModel(
        code=code,
        durability_days=durability_days,
    )
    session.add(new_promocode)
    await session.commit()
    return new_promocode


async def update(
        session: AsyncSession,
        promocode_id: int,
        update_context: dict,
) -> None:
    await session.execute(
        sql_update(PromocodeModel).where(PromocodeModel.promocode_id == promocode_id).values(
            update_context
        )
    )
    await session.commit()


async def delete(session: AsyncSession, promocode_id: int) -> None:
    await session.execute(
        sql_delete(PromocodeModel).where(PromocodeModel.promocode_id == promocode_id)
    )
    await session.commit()


async def get_all(session: AsyncSession,) -> list[PromocodeModel]:
    return cast(list[PromocodeModel], (
        await session.scalars(sql_select(PromocodeModel))
    ).all())


async def get_by_code(session: AsyncSession, code: str) -> PromocodeModel:
    return cast(list[PromocodeModel], (
        await session.scalars(
            sql_select(PromocodeModel).where((PromocodeModel.code == code))
        )
    ).all())[0]
