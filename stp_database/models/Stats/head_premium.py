"""Модели, связанные с сущностями премии руководителей."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class HeadPremium(Base):
    """Модель, представляющая сущность премии руководителя за месяц в БД.

    Args:
        fullname: ФИО руководителя

        flr: Значение показателя FLR
        flr_normative: Норматив показателя FLR
        flr_normative_rate: Процент выполнения норматива FLR
        flr_premium: Процент премии руководителя за FLR

        gok: Значение показателя ГОК
        gok_normative: Норматив показателя ГОК
        gok_normative_rate: Процент выполнения норматива ГОК
        gok_premium: Процент премии руководителя за ГОК

        target: Значение показателя спец. цели
        target_type: Тип спец. цели
        target_normative_first: Норматив показателя первой спец. цели
        target_normative_second: Норматив показателя второй спец. цели
        target_normative_rate_first: Процент выполнения норматива первой спец. цели
        target_normative_rate_second: Процент выполнения норматива второй спец. цели
        target_premium: Процент премии руководителя за спец. цель
        pers_target_manual: Тип спец. цели (Старое, не используется)


        head_adjust_premium: Ручная правка премии руководителем
        total_premium: Общий процент премии
        updated_at: Дата обновления показателей премии
        extraction_period: Дата, с которой производилась выгрузка премии

    Methods:
        __repr__(): Возвращает строковое представление объекта HeadPremium.
    """

    __tablename__ = "HeadPremium"

    employee_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
        comment="Идентификатор сотрудника на OKC",
    )

    flr: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя FLR"
    )
    flr_normative: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя FLR"
    )
    flr_normative_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива FLR",
    )
    flr_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за FLR",
    )

    gok: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя ГОК"
    )
    gok_normative: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя ГОК"
    )
    gok_normative_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива ГОК",
    )
    gok_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за ГОК",
    )

    target: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Значение показателя спец. цели",
    )
    target_type: Mapped[str | None] = mapped_column(
        Unicode(250),
        nullable=True,
        comment="Тип спец. цели",
    )
    target_normative_first: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Норматив показателя первой спец. цели",
    )
    target_normative_second: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Норматив показателя второй спец. цели",
    )
    target_normative_rate_first: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
    )
    target_normative_rate_second: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
    )
    target_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за спец. цель",
    )
    pers_target_manual: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Тип спец. цели (Старое, не используется)",
    )

    sl: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Значение показателя SL"
    )
    sl_normative_first: Mapped[int | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя первой цели SL"
    )
    sl_normative_second: Mapped[int | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя второй цели SL"
    )
    sl_normative_rate_first: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Процент выполнения норматива первой цели SL"
    )
    sl_normative_rate_second: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Процент выполнения норматива второй цели SL"
    )
    sl_premium: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Процент премии за SL"
    )

    head_adjust_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ручная правка премии руководителем",
    )
    total_premium: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Общий процент премии"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата обновления показателей премии",
        default=datetime.now,
    )
    extraction_period: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        primary_key=True,
        comment="Дата, с которой производилась выгрузка премии",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта HeadPremium."""
        return f"<HeadPremium employee_id={self.employee_id} total_premium={self.total_premium} updated_at={self.updated_at}>"
