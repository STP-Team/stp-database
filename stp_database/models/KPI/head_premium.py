"""Модели, связанные с сущностями премии руководителей."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column


class HeadPremium:
    """Модель, представляющая сущность премии руководителя за месяц в БД.

    Args:
        fullname: ФИО руководителя
        contacts_count: Кол-во контактов группы

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
        target_normative_rate_second: Процент выполнения норматива первой спец. цели
        target_premium: Процент премии руководителя за спец. цель
        pers_target_manual: Тип спец. цели (Старое, не используется)

        sales_count: Кол-во успешно закрытых продаж
        sales_potential: Кол-во потенциальных продаж

        head_adjust: Ручная правка премии руководителем
        total_premium: Общий процент премии
        updated_at: Дата обновления показателей премии

    Methods:
        __repr__(): Возвращает строковое представление объекта HeadPremium.
    """

    __tablename__ = "RgPremium"

    fullname: Mapped[str] = mapped_column(
        Unicode(250),
        nullable=False,
        name="FULLNAME",
        primary_key=True,
        comment="ФИО руководителя",
    )
    contacts_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Кол-во контактов группы", name="TC"
    )

    flr: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Значение показателя FLR", name="FLR"
    )
    flr_normative: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Норматив показателя FLR", name="FLR_NORMATIVE"
    )
    flr_normative_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива FLR",
        name="NORM_FLR",
    )
    flr_premium: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за FLR",
        name="PERC_FLR",
    )

    gok: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Значение показателя ГОК", name="GOK"
    )
    gok_normative: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Норматив показателя ГОК", name="GOK_NORMATIVE"
    )
    gok_normative_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива ГОК",
        name="NORM_GOK",
    )
    gok_premium: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за ГОК",
        name="PERC_GOK",
    )

    target: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Значение показателя спец. цели",
        name="PERS_FACT",
    )
    target_type: Mapped[Optional[str]] = mapped_column(
        Unicode(250),
        nullable=True,
        comment="Тип спец. цели",
        name="PERS_TARGET_TYPE_NAME",
    )
    target_normative_first: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Норматив показателя первой спец. цели",
        name="PERS_PLAN_1",
    )
    target_normative_second: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Норматив показателя второй спец. цели",
        name="PERS_PLAN_2",
    )
    target_normative_rate_first: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
        name="PERS_RESULT_1",
    )
    target_normative_rate_second: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
        name="PERS_RESULT_2",
    )
    target_premium: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии руководителя за спец. цель",
        name="PERS_PERCENT",
    )
    pers_target_manual: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Тип спец. цели (Старое, не используется)",
        name="PERS_TARGET_MANUAL",
    )

    sales_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во успешно закрытых продаж",
        name="SalesCount",
    )
    sales_potential: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во потенциальных продаж",
        name="SalesPotential",
    )

    head_adjust: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Ручная правка премии руководителем",
        name="HEAD_ADJUST",
    )
    total_premium: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Общий процент премии", name="TOTAL_PREMIUM"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        name="UpdateData",
        comment="Дата обновления показателей премии",
        default=datetime.now,
    )

    def __repr__(self):
        """Возвращает строковое представление объекта HeadPremium."""
        return f"<HeadPremium {self.fullname} {self.contacts_count} {self.total_premium} {self.updated_at}>"
