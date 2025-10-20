"""Модели, связанные с сущностями сотрудников."""

from typing import TYPE_CHECKING

from sqlalchemy import BIGINT, BOOLEAN, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stp_database.models.base import Base

if TYPE_CHECKING:
    from stp_database.models.STP.event_log import EventLog


class Employee(Base):
    """Модель, представляющий сущность сотрудника в БД.

    Args:
        id: Уникальный идентификатор пользователя
        user_id: Идентификатор сотрудника в Telegram
        username: Username сотрудника в Telegram
        division: Направление сотрудника (НТП/НЦК)
        position: Позиция/должность сотрудника
        fullname: ФИО сотрудника
        head: ФИО руководителя сотрудника
        email: Email сотрудника
        role: Уровень доступа сотрудника в БД
        is_trainee: Является ли сотрудник стажером
        is_casino_allowed: Разрешено ли казино сотруднику

    Methods:
        __repr__(): Возвращает строковое представление объекта Employee.
    """

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, comment="Уникальный идентификатор пользователя"
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT, nullable=True, comment="Идентификатор сотрудника в Telegram"
    )
    username: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Username сотрудника в Telegram"
    )
    division: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Направление сотрудника (НТП/НЦК)"
    )
    position: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Позиция/должность сотрудника"
    )
    fullname: Mapped[str] = mapped_column(
        Unicode, nullable=False, comment="ФИО сотрудника"
    )
    head: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="ФИО руководителя сотрудника"
    )
    email: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Email сотрудника"
    )
    role: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Уровень доступа сотрудника в БД"
    )
    is_trainee: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, default=True, comment="Является ли сотрудник стажером"
    )
    is_casino_allowed: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, comment="Разрешено ли казино сотруднику"
    )

    # Отношения
    event_logs: Mapped[list["EventLog"]] = relationship(
        "EventLog", back_populates="employee", lazy="select"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Employee."""
        return f"<Employee {self.id} {self.user_id} {self.username} {self.fullname} {self.head} {self.email} {self.role}>"
