"""Модели, связанные с сущностями настроек."""

import json
from datetime import datetime
from typing import Any, Dict

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
        get_values(): Получить настройки в виде словаря.
        set_values(values): Установить настройки из словаря.
        get_setting(key, default): Получить значение конкретной настройки.
        set_setting(key, value): Установить значение конкретной настройки.
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

    def get_values(self) -> Dict[str, Any]:
        """Получить настройки в виде словаря.

        Returns:
            Словарь с настройками
        """
        try:
            return json.loads(self.values)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_values(self, values: Dict[str, Any]) -> None:
        """Установить настройки из словаря.

        Args:
            values: Словарь с настройками
        """
        self.values = json.dumps(values, ensure_ascii=False)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получить значение конкретной настройки.

        Args:
            key: Ключ настройки
            default: Значение по умолчанию, если ключ не найден

        Returns:
            Значение настройки или default
        """
        values = self.get_values()
        return values.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Установить значение конкретной настройки.

        Args:
            key: Ключ настройки
            value: Новое значение
        """
        values = self.get_values()
        values[key] = value
        self.set_values(values)
