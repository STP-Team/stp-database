"""Модели, связанные с сущностями сотрудников."""

from sqlalchemy import BIGINT, BOOLEAN, Boolean, Unicode
from sqlalchemy.orm import Mapped, mapped_column


class Employee:
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

    Methods:
        __repr__(): Возвращает строковое представление объекта Employee.
    """

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=True)
    username: Mapped[str] = mapped_column(Unicode, nullable=True)
    division: Mapped[str] = mapped_column(Unicode, nullable=True)
    position: Mapped[str] = mapped_column(Unicode, nullable=True)
    fullname: Mapped[str] = mapped_column(Unicode, nullable=False)
    head: Mapped[str] = mapped_column(Unicode, nullable=True)
    email: Mapped[str] = mapped_column(Unicode, nullable=True)
    role: Mapped[int] = mapped_column(BIGINT, nullable=False)
    is_trainee: Mapped[Boolean] = mapped_column(BOOLEAN, nullable=False, default=True)
    is_casino_allowed: Mapped[Boolean] = mapped_column(BOOLEAN, nullable=False)

    def __repr__(self):
        """Возвращает строковое представление объекта Employee."""
        return f"<Employee {self.id} {self.user_id} {self.username} {self.fullname} {self.head} {self.email} {self.role}>"
