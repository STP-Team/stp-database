"""Модели, связанные с сущностями графиков."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BIGINT, TIMESTAMP, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Schedule(Base):
    """Модель, представляющая сущность графиков в БД.

    Args:
        id: Уникальный идентификатор графика
        file_id: Идентификатор Telegram загруженного файла
        file_name: Название загруженного файла
        file_size: Размер файла в байтах
        uploaded_by_user_id: Идентификатор Telegram сотрудника, загрузившего файл
        uploaded_at: Время загрузки файла

    Methods:
        __repr__(): Возвращает строковое представление объекта Schedule.
    """

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор графика",
    )
    file_id: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Идентификатор Telegram загруженного файла"
    )
    file_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Название загруженного файла"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        BIGINT, nullable=True, comment="Размер файла в байтах"
    )
    uploaded_by_user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="Идентификатор Telegram сотрудника, загрузившего файл",
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Время загрузки файла",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Schedule."""
        return f"<ScheduleLog {self.id} {self.file_id} {self.file_name} {self.file_size} {self.uploaded_by_user_id} {self.uploaded_at}>"
