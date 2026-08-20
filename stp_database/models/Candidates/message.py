"""Модель сообщения кандидата."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Message(Base):
    """Сообщение в диалоге с кандидатом."""

    __tablename__ = "messages"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    uuid: Mapped[str] = mapped_column(
        String(250),
        primary_key=True,
        nullable=False,
    )

    candidate_uuid: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sended_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    meta: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="{}",
    )

    def __repr__(self) -> str:
        return (
            f"<Message uuid={self.uuid} "
            f"candidate_uuid={self.candidate_uuid} "
            f"sender_id={self.sender_id}>"
        )