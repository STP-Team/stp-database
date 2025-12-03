"""Модели, связанные с сущностями пар сообщений."""

from datetime import datetime

from sqlalchemy import BIGINT, DateTime, Index, Unicode, text
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class MessagesPair(Base):
    """Модель, представляющая сущность пары сообщений в БД.

    Args:
        id: Уникальный идентификатор записи
        user_chat_id: Идентификатор чата пользователя
        user_message_id: Идентификатор сообщения пользователя
        topic_chat_id: Идентификатор чата темы
        topic_message_id: Идентификатор сообщения темы
        topic_thread_id: Идентификатор треда темы
        question_token: Токен вопроса
        direction: Направление сообщения
        created_at: Дата и время создания

    Methods:
        __repr__(): Возвращает строковое представление объекта MessagesPair.
    """

    __tablename__ = "messages_pairs"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        comment="Уникальный идентификатор записи",
        autoincrement=True,
    )
    user_chat_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор чата пользователя"
    )
    user_message_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор сообщения пользователя"
    )
    topic_chat_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор чата темы"
    )
    topic_message_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор сообщения темы"
    )
    topic_thread_id: Mapped[int] = mapped_column(
        BIGINT, nullable=True, comment="Идентификатор темы"
    )
    question_token: Mapped[str] = mapped_column(
        Unicode(255), nullable=False, comment="Токен вопроса"
    )
    direction: Mapped[str] = mapped_column(
        Unicode(20), nullable=False, comment="Направление сообщения"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Дата и время создания",
    )

    __table_args__ = (
        Index("ix_messages_pairs_created_at", "created_at"),
        Index("ix_messages_pairs_question_token", "question_token"),
        Index(
            "ix_messages_pairs_topic_chat_message", "topic_chat_id", "topic_message_id"
        ),
        Index("ix_messages_pairs_user_chat_message", "user_chat_id", "user_message_id"),
    )

    def __repr__(self):
        """Возвращает строковое представление объекта MessagesPair."""
        return f"<MessagesPair {self.id} {self.question_token} {self.direction}>"
