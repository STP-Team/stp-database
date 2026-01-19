"""Модели, связанные с результатами обучения."""

from datetime import datetime

from sqlalchemy import BIGINT, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base, int_pk


class Result(Base):
    """Модель, представляющая результаты прохождения обучения.

    Args:
        id: Уникальный идентификатор результата
        user_id: Идентификатор пользователя
        first_q: Ответ на первый вопрос
        second_q: Ответ на второй вопрос
        third_q: Ответ на третий вопрос
        fourth_q: Ответ на четвертый вопрос
        fifth_q: Ответ на пятый вопрос
        sixth_q: Ответ на шестой вопрос
        started_at: Время начала прохождения
        ended_at: Время окончания прохождения

    Methods:
        __repr__(): Возвращает строковое представление объекта Result.
    """

    __tablename__ = "results"

    id: Mapped[int_pk]

    user_id: Mapped[int | None] = mapped_column(
        BIGINT, nullable=True, comment="Идентификатор пользователя"
    )
    first_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на первый вопрос"
    )
    second_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на второй вопрос"
    )
    third_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на третий вопрос"
    )
    fourth_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на четвертый вопрос"
    )
    fifth_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на пятый вопрос"
    )
    sixth_q: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Ответ на шестой вопрос"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Время начала прохождения"
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="Время окончания прохождения"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Result."""
        return f"<Result {self.user_id} {self.started_at} {self.ended_at}>"
