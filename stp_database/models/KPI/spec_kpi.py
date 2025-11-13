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

        kpi_extract_date: Дата, с которой производилась выгрузка показателей
        updated_at: Дата выгрузки показателей в БД

    Methods:
        __repr__(): Возвращает строковое представление объекта SpecKPI.
    """

    __tablename__ = None  # Будет установлено динамически
    __abstract__ = True  # Абстрактная модель

    fullname: Mapped[str] = mapped_column(
        Unicode(250),
        nullable=False,
        name="FULLNAME",
        comment="ФИО специалиста",
        primary_key=True,
    )
    contacts_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Кол-во контактов специалиста", name="TC"
    )

    aht: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Значение показателя AHT за период", name="AHT"
    )
    flr: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя FLR за период", name="FLR"
    )
    csi: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Значение показателя оценки за период", name="CSI"
    )
    pok: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Значение показателя отклика за период",
        name="POK",
    )
    delay: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Значение показателя задержки за период (только НТП)",
        name="DELAY",
    )

    sales_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во реальных продаж за период",
        name="SalesCount",
        default=0,
    )
    sales_potential: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Кол-во потенциальных продаж за период",
        name="SalesPotential",
    )
    sales_conversion: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Конверсия продаж",
        name="SalesConversion",
    )

    paid_service_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Количество закрытых заявок на платный сервис",
        name="PaidServiceCount",
        default=0,
    )
    paid_service_conversion: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Конверсия платного сервиса",
        name="PaidServiceConversion",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата выгрузки показателей в БД",
        name="UpdateData",
        default=datetime.now,
    )
    kpi_extract_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата, с которой производилась выгрузка показателей",
        name="KpiExtractDate",
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта SpecKPI."""
        table = self.__tablename__ or "Unknown"
        return f"<SpecKPI[{table}] {self.fullname} {self.contacts_count} {self.kpi_extract_date} {self.updated_at}>"


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
