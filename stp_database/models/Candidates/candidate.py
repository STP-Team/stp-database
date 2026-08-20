"""Модель кандидата."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Candidate(Base):
    """Кандидат в системе найма."""

    __tablename__ = "candidate"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    uuid: Mapped[str] = mapped_column(
        String(250),
        primary_key=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "new",
            "form_wait",
            "form_rejected",
            "hr_wait",
            "hr_rejected",
            "meet_approved",
            "meet_rejected",
            "meet_accepted",
        ),
        nullable=False,
        default="new",
        server_default="new",
    )

    fullname: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    short_link: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    use_password: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    form_uuid: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    form_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    readed_message_user_uuid: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    readed_message_candidate_uuid: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<Candidate uuid={self.uuid} "
            f"fullname={self.fullname} "
            f"status={self.status}>"
        )