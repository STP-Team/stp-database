"""Модель событий, связанных с действиями сотрудников."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BIGINT, JSON, TIMESTAMP, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stp_database.models.base import Base

if TYPE_CHECKING:
    from stp_database.models.STP.employee import Employee


class EventLog(Base):
    """Модель, представляющая запись события, связанного с сотрудником.

    Args:
        id: Уникальный идентификатор события
        user_id: Идентификатор сотрудника (внешний ключ на таблицу employees)
        event_type: Тип события (например, 'click', 'login', 'logout')
        event_category: Категория события (например, 'UI', 'System', 'Network')
        timestamp: Время регистрации события
        session_id: Идентификатор сессии, к которой относится событие
        dialog_state: Состояние диалога на момент события
        window_name: Имя окна или экрана, где произошло событие
        action: Действие, совершённое пользователем
        metadata: Дополнительные данные в формате JSON

    Relationships:
        employee: Объект `Employee`, связанный с данным событием

    Indexes:
        idx_user_id: (user_id)
        idx_event_type: (event_type)
        idx_event_category: (event_category)
        idx_timestamp: (timestamp)
        idx_session_id: (session_id)
        idx_user_time: (user_id, timestamp)
        idx_category_time: (event_category, timestamp)
        idx_type_time: (event_type, timestamp)
    """

    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор события",
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("employees.user_id", name="fk_event_logs_user"),
        nullable=True,
        comment="Идентификатор сотрудника (внешний ключ на таблицу employees)",
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="Тип события (click/login/logout и т.п.)",
    )
    event_category: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
        comment="Категория события (UI/System/Network и т.п.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=True,
        comment="Время регистрации события",
    )
    session_id: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Идентификатор сессии"
    )

    dialog_state: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Состояние диалога на момент события"
    )
    window_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Имя окна/экрана, где произошло событие"
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Действие, совершённое пользователем"
    )

    event_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        comment="Дополнительные данные события в формате JSON",
    )

    # Отношения
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="event_logs", lazy="joined"
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_category", "event_category"),
        Index("idx_timestamp", "timestamp"),
        Index("idx_session_id", "session_id"),
        Index("idx_user_time", "user_id", "timestamp"),
        Index("idx_category_time", "event_category", "timestamp"),
        Index("idx_type_time", "event_type", "timestamp"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта EventLog."""
        return (
            f"<EventLog id={self.id}, user_id={self.user_id}, type={self.event_type}, "
            f"category={self.event_category}, timestamp={self.timestamp}>"
        )
