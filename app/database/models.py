from typing import Optional, Any

from sqlalchemy import String, BigInteger, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.orm import Mapped, mapped_column


from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)

    full_name: Mapped[str] = mapped_column(String(50), nullable=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    points: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default="0")

    gpt_premium: Mapped[bool] = mapped_column(default=False, server_default="false")
    free_gpt_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    payment_datetime: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)  # ?
    payment_until: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)  # ?

    ukr_tests_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")
    math_tests_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")
    hist_tests_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")

    ukr_exercises_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")
    math_exercises_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")
    hist_exercises_done: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False, server_default="{}")


class TestModel(Base):
    __tablename__ = "tests"

    test_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)

    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subject: Mapped[int] = mapped_column(Integer)

    exercises_quantity: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")

    is_available: Mapped[bool] = mapped_column(default=False, server_default="false")


class ExerciseModel(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
    test_id: Mapped[int] = mapped_column(BigInteger)

    number: Mapped[int] = mapped_column(BigInteger)
    photo_id: Mapped[str] = mapped_column(String(100))
    exercise_type: Mapped[int] = mapped_column(Integer)
    options: Mapped[Optional[int]] = mapped_column(Integer)
    correct_answer_list: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    correct_answer_str: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    correct_answer_int: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    educational_material: Mapped[str] = mapped_column(Text(), nullable=True)


class PromocodeModel(Base):
    __tablename__ = "promocodes"

    promocode_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)

    code: Mapped[str] = mapped_column(String(50))
    durability_days: Mapped[int] = mapped_column(Integer, nullable=False)
