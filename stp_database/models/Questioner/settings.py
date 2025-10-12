"""Модели, связанные с сущностями настроек."""

from datetime import datetime

from sqlalchemy import BIGINT, DateTime, Index, Unicode, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Settings(Base):
    """Модель, представляющая сущность настроек в БД.

    Args:
        id: Уникальный идентификатор записи
        group_id: Идентификатор группы
        group_name: Название группы
        values: Значения настроек в формате JSON
        last_update: Дата и время последнего обновления

    Methods:
        __repr__(): Возвращает строковое представление объекта Settings.
    """

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        comment="Уникальный идентификатор записи",
        autoincrement=True,
    )
    group_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор группы Telegram"
    )
    group_name: Mapped[str] = mapped_column(
        Unicode(255), nullable=False, comment="Название группы"
    )
    values: Mapped[str] = mapped_column(
        Unicode(4000),
        nullable=False,
        server_default=text("'{}'"),
        comment="Значения настроек в формате JSON",
    )
    last_update: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Дата и время последнего обновления",
    )

    __table_args__ = (
        UniqueConstraint("group_id", name="uq_settings_group_id"),
        Index("ix_settings_group_id", "group_id"),
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Settings."""
        return f"<Settings {self.id} group_id={self.group_id} {self.group_name}>"
