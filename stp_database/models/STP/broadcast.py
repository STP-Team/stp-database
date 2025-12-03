"""Модели, связанные с сущностями рассылок."""

from typing import List

from sqlalchemy import BIGINT, JSON, TIMESTAMP, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Broadcast(Base):
    """Модель, представляющая сущность рассылки в БД.

    Args:
        id: Уникальный идентификатор рассылки
        user_id: Идентификатор Telegram владельца рассылки
        type: Тип рассылки: all, division, role или group
        target: Конкретная цель рассылки: подразделение (НЦК, НТП1, НТП2) или выбранная группа
        text: Текст рассылки
        recipients: Список user_id для рассылки
        created_at: Время создания рассылки

    Methods:
        __repr__(): Возвращает строковое представление объекта Broadcast.
    """

    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор рассылки",
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор Telegram владельца рассылки"
    )
    type: Mapped[str] = mapped_column(
        Enum("all", "division", "role", "group"),
        nullable=False,
        comment="Тип рассылки: all, division, role или group",
    )
    target: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Конкретная цель рассылки: подразделение (НЦК, НТП1, НТП2) или выбранная группа",
    )
    text: Mapped[str] = mapped_column(Text, nullable=False, comment="Текст рассылки")
    recipients: Mapped[List[int] | None] = mapped_column(
        JSON, nullable=True, comment="Список user_id для рассылки"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Время создания рассылки",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Broadcast."""
        return f"<Broadcast {self.id} {self.user_id} {self.type} {self.target} {self.created_at}>"

    def to_dict(self):
        """Преобразует объект Broadcast в словарь."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "target": self.target,
            "text": self.text,
            "recipients": self.recipients,
            "created_at": self.created_at,
        }
