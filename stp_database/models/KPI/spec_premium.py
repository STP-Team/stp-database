"""Модели, связанные с сущностями премии специалистов."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class SpecPremium(Base):
    """Модель, представляющая сущность премии специалиста за месяц в БД.

    Args:
        fullname: ФИО специалиста
        contacts_count: Кол-во контактов специалиста

        delay: Средняя задержка (только НТП)
        appeals_dw_perc: Процент сорванных контактов
        routing_perc: Процент переводов контактов

        csi: Значение показателя оценки
        csi_normative: Норматив показателя оценки
        csi_normative_rate: Процент выполнения норматива оценки
        csi_premium: Процент премии специалиста за оценку

        csi_response: Значение показателя отклика
        csi_response_normative: Норматив показатели отклика
        csi_response_rate: Процент выполнения норматива отклика

        flr: Значение показателя FLR
        flr_normative: Норматив показателя FLR
        flr_normative_rate: Процент выполнения норматива FLR
        flr_premium: Процент премии специалиста за FLR

        gok: Значение показателя ГОК
        gok_normative: Норматив показателя ГОК
        gok_normative_rate: Процент выполнения норматива ГОК
        gok_premium: Процент премии специалиста за ГОК

        target: Значение показателя спец. цели
        target_type: Тип спец. цели
        target_normative_first: Норматив показателя первой спец. цели
        target_normative_second: Норматив показателя второй спец. цели
        target_normative_rate_first: Процент выполнения норматива первой спец. цели
        target_normative_rate_second: Процент выполнения норматива второй спец. цели
        target_premium: Процент премии специалиста за спец. цель
        pers_target_manual: Тип спец. цели (Старое, не используется)

        discipline_premium: Процент премии за дисциплину
        tests_premium: Процент премии за тестирования
        thanks_premium: Процент премии за благодарности клиентов
        tutors_premium: Процент премии за посещение обучений

        head_adjust_premium: Ручная правка премии руководителем
        total_premium: Общий процент премии
        updated_at: Дата обновления показателей премии
        kpi_extract_date: Дата, с которой производилась выгрузка премии

    Methods:
        __repr__(): Возвращает строковое представление объекта SpecPremium.
    """

    __tablename__ = "SpecPremium"

    fullname: Mapped[str] = mapped_column(
        Unicode(250),
        nullable=False,
        name="FULLNAME",
        primary_key=True,
        comment="ФИО специалиста",
    )
    contacts_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во контактов специалиста", name="TC"
    )

    csi: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя оценки", name="CSI"
    )
    csi_normative: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Норматив показатели оценки", name="CSI_NORMATIVE"
    )
    csi_normative_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива оценки",
        name="NORM_CSI",
    )
    csi_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии специалиста за оценку",
        name="PERC_CSI",
    )

    csi_response: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя отклика", name="CSI_RESPONSE"
    )
    csi_response_normative: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Норматив показатели отклика",
        name="CSI_RESPONSE_NORMATIVE",
    )
    csi_response_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива отклика",
        name="NORM_CSI_RESPONSE",
    )

    flr: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя FLR", name="FLR"
    )
    flr_normative: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя FLR", name="FLR_NORMATIVE"
    )
    flr_normative_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива FLR",
        name="NORM_FLR",
    )
    flr_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии специалиста за FLR",
        name="PERC_FLR",
    )

    gok: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя ГОК", name="GOK"
    )
    gok_normative: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Норматив показателя ГОК", name="GOK_NORMATIVE"
    )
    gok_normative_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива ГОК",
        name="NORM_GOK",
    )
    gok_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии специалиста за ГОК",
        name="PERC_GOK",
    )

    target: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя спец. цели", name="PERS_FACT"
    )
    target_type: Mapped[str | None] = mapped_column(
        Unicode(250),
        nullable=True,
        comment="Тип спец. цели",
        name="PERS_TARGET_TYPE_NAME",
    )
    target_normative_first: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Норматив показателя первой спец. цели",
        name="PERS_PLAN_1",
    )
    target_normative_second: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Норматив показателя второй спец. цели",
        name="PERS_PLAN_2",
    )
    target_normative_rate_first: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
        name="PERS_RESULT_1",
    )
    target_normative_rate_second: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Процент выполнения норматива первой спец. цели",
        name="PERS_RESULT_2",
    )
    target_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии специалиста за спец. цель",
        name="PERS_PERCENT",
    )
    pers_target_manual: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Тип спец. цели (Старое, не используется)",
        name="PERS_TARGET_MANUAL",
    )

    discipline_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии за дисциплину",
        name="PERC_DISCIPLINE",
    )
    tests_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии за тестирования",
        name="PERC_TESTING",
    )
    thanks_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии за благодарности клиентов",
        name="PERC_THANKS",
    )
    tutors_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Процент премии за посещение обучений",
        name="PERC_TUTORS",
    )

    head_adjust_premium: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ручная правка премии руководителем",
        name="HEAD_ADJUST",
    )
    total_premium: Mapped[float | None] = mapped_column(
        Integer, nullable=True, comment="Общий процент премии", name="TOTAL_PREMIUM"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата обновления показателей премии",
        name="UpdateData",
        default=datetime.now,
    )
    kpi_extract_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата, с которой производилась выгрузка премии",
        name="KpiExtractDate",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта SpecPremium."""
        return f"<SpecPremium {self.fullname} {self.contacts_count} {self.total_premium} {self.updated_at}>"
