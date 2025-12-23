"""Модели, связанные с сущностями SL."""

from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class AssignedTest(Base):
    """Модель, представляющая сущность назначенных тестов.

    Methods:
        __repr__(): Возвращает строковое представление объекта AssignedTest.
    """

    __tablename__ = "TestsAssigned"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    test_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Идентификатор теста"
    )
    test_name: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, comment="Название теста"
    )
    employee_fullname: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, comment="ФИО сотрудника, кому назначен тест"
    )
    head_fullname: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО руководителя сотрудника"
    )
    creator_fullname: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО создателя теста"
    )
    status: Mapped[str | None] = mapped_column(
        VARCHAR(255), nullable=True, comment="Статус теста"
    )
    active_from: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Дата назначения теста"
    )

    extraction_period: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата начала периода выгрузки",
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата создания записи",
        default=datetime.now,
    )

    def __repr__(self):
        """Возвращает строковое представление объекта AssignedTest."""
        return f"<AssignedTest {self.test_name} {self.employee_fullname} {self.status}>"
