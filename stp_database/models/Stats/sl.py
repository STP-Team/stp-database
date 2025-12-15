"""Модели, связанные с сущностями премии руководителей."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class SL(Base):
    """Модель, представляющая сущность ServiceLevel за день в БД.

    Methods:
        __repr__(): Возвращает строковое представление объекта HeadPremium.
    """

    __tablename__ = "SL"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    sl: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение SL"
    )

    sl_contacts: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Контактов, учтенных в SL"
    )
    received_contacts: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во поступивших контактов"
    )

    accepted_contacts: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во принятых контактов"
    )
    accepted_contacts_percent: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Процент принятых контактов"
    )

    missed_contacts: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во пропущенных контактов"
    )
    missed_contacts_percent: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Процент пропущенных контактов"
    )

    average_proc_time: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Среднее время обработки контактов"
    )

    extraction_period: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата, с которой производилась выгрузка премии",
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата обновления показателей SL",
        default=datetime.now,
    )

    def __repr__(self):
        """Возвращает строковое представление объекта SL."""
        return f"<SL {self.extraction_period} {self.sl} {self.sl_contacts}>"
