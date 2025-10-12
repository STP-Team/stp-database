"""Модели, связанные с сущностями событий."""

from datetime import datetime

from sqlalchemy import BOOLEAN, DateTime, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Event(Base):
    """Модель, представляющая сущность события в БД.

    Args:
        id: Уникальный идентификатор события
        event_name: Название события
        sum: Сумма события
        is_published: Опубликовано ли событие
        payment_link: Ссылка для оплаты
        event_date: Дата события

    Methods:
        __repr__(): Возвращает строковое представление объекта Event.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор события",
        autoincrement=True,
    )
    event_name: Mapped[str] = mapped_column(
        Unicode(250), nullable=True, comment="Название события"
    )
    sum: Mapped[int] = mapped_column(Integer, nullable=True, comment="Сумма события")
    is_published: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Опубликовано ли событие"
    )
    payment_link: Mapped[str] = mapped_column(
        Unicode(500), nullable=True, comment="Ссылка для оплаты"
    )
    event_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="Дата события"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Event."""
        return f"<Event {self.id} {self.event_name} {self.event_date}>"
