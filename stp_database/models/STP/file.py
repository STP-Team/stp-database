"""Модели, связанные с сущностями файлов."""

from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class File(Base):
    """Модель, представляющая сущность файла в БД.

    Args:
        id: Уникальный идентификатор файла
        file_id: Идентификатор Telegram загруженного файла
        file_name: Название загруженного файла
        file_size: Размер файла в байтах
        uploaded_by_user_id: Идентификатор Telegram сотрудника, загрузившего файл
        uploaded_at: Время загрузки файла

    Methods:
        __repr__(): Возвращает строковое представление объекта File.
    """

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор файла",
    )
    file_id: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Идентификатор Telegram загруженного файла"
    )
    file_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Название загруженного файла"
    )
    file_size: Mapped[int | None] = mapped_column(
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
        """Возвращает строковое представление объекта File."""
        return f"<File {self.id} {self.file_id} {self.file_name} {self.file_size} {self.uploaded_by_user_id} {self.uploaded_at}>"
