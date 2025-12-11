"""Модели, связанные с сущностями показателей специалистов."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class SpecKPI(Base):
    """Универсальная модель, представляющая сущность показателей специалиста день, неделю или месяц.

    Может работать с разными таблицами: KpiDay, KpiWeek, KpiMonth.
    Таблица указывается динамически через __table_args__ или при создании мапера.

    Args:
        fullname: ФИО специалиста
        contacts_count: Кол-во контактов специалиста

        aht: Значение показателя AHT за период
        flr: Значение показателя FLR за период
        csi: Значение показателя оценки за период
        pok: Значение показателя отклика за период
        delay: Значение показателя задержки за период (только НТП)

        sales_count: Кол-во реальных продаж за период
        sales_potential: Кол-во потенциальных продаж за период
        sales_conversion: Конверсия продаж

        paid_service_count: Платный сервис реальный
        paid_service_conversion: Конверсия платного сервиса

        extraction_period: Дата, с которой производилась выгрузка показателей
        updated_at: Дата выгрузки показателей в БД

    Methods:
        __repr__(): Возвращает строковое представление объекта SpecKPI.
    """

    __tablename__ = None  # Будет установлено динамически
    __abstract__ = True  # Абстрактная модель

    fullname: Mapped[str] = mapped_column(
        Unicode(250),
        nullable=False,
        comment="ФИО специалиста",
        primary_key=True,
    )
    contacts_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во контактов специалиста за период"
    )

    aht: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Значение показателя AHT за период"
    )
    flr: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя FLR за период"
    )
    csi: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя оценки за период"
    )
    pok: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Значение показателя отклика за период",
    )
    delay: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Значение показателя задержки за период",
    )

    sales_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во реальных продаж за период",
        default=0,
    )
    sales_potential: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во потенциальных продаж за период",
    )
    sales_conversion: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Конверсия продаж за период",
    )

    paid_service_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Количество закрытых заявок на платный сервис за период",
        default=0,
    )
    paid_service_conversion: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Конверсия платного сервиса за период",
    )

    extraction_period: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата, с которой производилась выгрузка отчета",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата выгрузки показателей в БД",
        default=datetime.now,
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта SpecKPI."""
        table = self.__tablename__
        return f"<SpecKPI[{table}] {self.fullname} {self.contacts_count} {self.extraction_period} {self.updated_at}>"


# Конкретные модели для каждой таблицы
class SpecDayKPI(SpecKPI):
    """Модель показателей специалиста за день."""

    __tablename__ = "KpiDay"


class SpecWeekKPI(SpecKPI):
    """Модель показателей специалиста за неделю."""

    __tablename__ = "KpiWeek"


class SpecMonthKPI(SpecKPI):
    """Модель показателей специалиста за месяц."""

    __tablename__ = "KpiMonth"
