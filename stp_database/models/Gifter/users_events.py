"""Модели, связанные с сущностями связей пользователей и событий."""

from sqlalchemy import BOOLEAN, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class UserEvent(Base):
    """Модель, представляющая сущность связи пользователя и события в БД.

    Args:
        id: Уникальный идентификатор записи
        user_id: Идентификатор пользователя
        event_id: Идентификатор события
        paid: Оплачено ли участие

    Methods:
        __repr__(): Возвращает строковое представление объекта UserEvent.
    """

    __tablename__ = "users_event"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор записи",
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Идентификатор пользователя"
    )
    event_id: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Идентификатор события"
    )
    paid: Mapped[Boolean] = mapped_column(
        BOOLEAN, nullable=True, comment="Оплачено ли участие"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта UserEvent."""
        return f"<UserEvent {self.id} user_id={self.user_id} event_id={self.event_id} paid={self.paid}>"
