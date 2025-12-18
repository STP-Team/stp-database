"""Модели, связанные с сущностями графиков наставников."""

from datetime import datetime

from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class TutorsSchedule(Base):
    """Модель, представляющая сущность графика наставника.

    Methods:
        __repr__(): Возвращает строковое представление объекта TutorsSchedule.
    """

    __tablename__ = "TutorsSchedule"

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True,
        comment="Уникальный идентификатор графика",
        autoincrement=True,
    )

    tutor_employee_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Идентификатор наставника OKC"
    )
    tutor_fullname: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО наставника"
    )
    tutor_division: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="Направление наставника"
    )

    trainee_employee_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Идентификатор стажера OKC"
    )
    trainee_fullname: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО стажера"
    )
    trainee_type: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Тип стажера"
    )

    training_day: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True, comment="День обучения"
    )
    training_start_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True, comment="Время начала обучения"
    )
    training_end_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True, comment="Время конца обучения"
    )

    extraction_period: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        comment="Дата начала выгрузки",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        comment="Дата создания",
        default=datetime.now,
    )

    def __repr__(self):
        """Возвращает строковое представление объекта TutorsSchedule."""
        return f"<TutorsSchedule {self.extraction_period} {self.tutor_fullname} {self.trainee_fullname} {self.training_day}>"
