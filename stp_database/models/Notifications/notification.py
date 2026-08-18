"""Модели внутренней системы уведомлений STPsher."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BIGINT,
    JSON,
    TIMESTAMP,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Notification(Base):
    """
    Уведомление STPsher.

    Сам текст хранится один раз.
    Получатели хранятся отдельно
    в NotificationRecipient.
    """

    __tablename__ = "notifications"

    __table_args__ = (
        Index(
            "ix_notifications_created_at",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный ID уведомления",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Заголовок уведомления",
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст уведомления",
    )

    type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="info",
        comment=(
            "Тип уведомления: "
            "info, system, achievement, schedule и т.д."
        ),
    )

    action: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        default=None,
        comment=(
            "Действие при нажатии "
            "на уведомление"
        ),
    )

    action_data: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment=(
            "Дополнительные данные "
            "для действия уведомления"
        ),
    )

    created_by: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        default=None,
        comment=(
            "Логический employees.id "
            "создателя уведомления"
        ),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Дата создания уведомления",
    )


class NotificationRecipient(Base):
    """
    Получатель уведомления.
    """

    __tablename__ = "notification_recipients"

    __table_args__ = (
        Index(
            "ix_notification_recipients_employee_read",
            "employee_id",
            "read_at",
        ),
    )

    notification_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        comment="ID уведомления",
    )

    employee_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        comment=(
            "employees.id получателя "
            "из основной БД STP"
        ),
    )

    read_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        default=None,
        comment="Дата первого прочтения",
    )