"""Модели для системы сделки сменами (биржи смен)."""

import json
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    DATE,
    JSON,
    TIME,
    TIMESTAMP,
    Enum,
    Index,
    Integer,
    String,
    TypeDecorator,
    Unicode,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stp_database.models.base import Base


class UnicodeJSON(TypeDecorator):
    """A JSON type that properly handles Unicode characters without escaping.

    This type ensures that Cyrillic and other non-ASCII characters are stored
    as readable text in JSON fields instead of Unicode escape sequences.

    Also handles cases where data might be pre-serialized by drivers.
    """

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Optional[Any], dialect) -> Optional[str]:
        """Process value before saving to database."""
        if value is None:
            return None

        # If it's already a string (pre-serialized by driver), don't double-encode
        if isinstance(value, str):
            try:
                # Try to parse and re-serialize with proper Unicode handling
                parsed = json.loads(value)
                return json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
            except json.JSONDecodeError:
                # If it's not valid JSON, treat as raw string
                return value

        # Normal case: serialize Python object
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def process_result_value(self, value: Optional[str], dialect) -> Optional[Any]:
        """Process value when loading from database."""
        if value is None:
            return None

        # If value is already a Python object (list, dict, etc.), return as-is
        if not isinstance(value, (str, bytes, bytearray)):
            return value

        return json.loads(value)


if TYPE_CHECKING:
    from stp_database.models.STP.employee import Employee


class Exchange(Base):
    """Модель сделки сменой или частью смены.

    Представляет объявление о продаже/обмене смены на бирже.

    Args:
        id: Уникальный идентификатор сделки
        owner_id: Идентификатор владельца объявления (кто создал сделку)
        counterpart_id: Идентификатор второй стороны (кто принял сделку)
        start_time: Начало смены
        end_time: Окончание смены (если частичная смена)
        price: Цена за смену или часть смены
        comment: Комментарий к сделке
        owner_intent: Намерение владельца (sell, buy)
        status: Статус сделки (active, sold, cancelled)
        is_private: Является ли подмена приватной
        is_paid: Отметка о наличии оплаты
        payment_type: Тип оплаты (immediate, on_date)
        payment_date: Конкретная дата оплаты
        created_at: Время создания объявления
        updated_at: Время последнего обновления
        sold_at: Время продажи

    Relationships:
        owner: Объект Employee владельца объявления
        counterpart: Объект Employee второй стороны
        subscriptions: Подписки на этот сделка

    Indexes:
        idx_owner_id: (owner_id)
        idx_counterpart_id: (counterpart_id)
        idx_status: (status)
        idx_start_time: (start_time)
        idx_created_at: (created_at)
        idx_status_start_time: (status, start_time)
        idx_owner_status: (owner_id, status)
    """

    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор сделки",
    )

    # Участники сделки
    owner_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="Идентификатор владельца объявления (кто создал сделку)",
    )
    counterpart_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор второй стороны (кто принял сделку)",
    )

    # Информация о смене
    start_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Начало смены",
    )
    end_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Окончание смены (если частичная смена)",
    )

    # Финансовая информация
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Цена за сделку",
    )
    is_paid: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Отметка о наличии оплаты",
    )
    payment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="immediate",
        comment="Тип оплаты (immediate, on_date)",
    )
    payment_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Конкретная дата оплаты (если payment_type равен 'on_date')",
    )

    # Тип и статус
    owner_intent: Mapped[str] = mapped_column(
        Enum("sell", "buy"),
        nullable=False,
        default="sell",
        comment="Намерение владельца: sell - предлагает свою смену, buy - хочет купить смену",
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", "sold", "canceled", "expired"),
        nullable=False,
        default="active",
        comment="Статус сделки (active, inactive, sold, canceled, expired)",
    )
    is_private: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Является ли подмена приватной (для отправки в личные сообщения)",
    )
    in_owner_schedule: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Показывать ли в графике владельца сделки",
    )
    in_counterpart_schedule: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Показывать ли в графике второй стороны",
    )

    # Дополнительная информация
    comment: Mapped[str | None] = mapped_column(
        Unicode(500),
        nullable=True,
        comment="Комментарий к сделке",
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Время создания объявления",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="Время последнего обновления",
    )
    sold_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Время продажи",
    )

    # Отношения
    owner: Mapped["Employee"] = relationship(
        "Employee",
        primaryjoin="foreign(Exchange.owner_id) == Employee.user_id",
        back_populates="owned_exchanges",
        lazy="joined",
    )
    counterpart: Mapped["Employee"] = relationship(
        "Employee",
        primaryjoin="foreign(Exchange.counterpart_id) == Employee.user_id",
        back_populates="counterpart_exchanges",
        lazy="joined",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_owner_id", "owner_id"),
        Index("idx_counterpart_id", "counterpart_id"),
        Index("idx_status", "status"),
        Index("idx_start_time", "start_time"),
        Index("idx_created_at", "created_at"),
        Index("idx_status_start_time", "status", "start_time"),
        Index("idx_owner_status", "owner_id", "status"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    @property
    def working_hours(self) -> float | None:
        """Количество рабочих часов между start_time и end_time."""
        if not self.start_time or not self.end_time:
            return None
        duration = self.end_time - self.start_time
        return round(duration.total_seconds() / 3600, 2)

    @property
    def total_price(self) -> float | None:
        """Вычисляет полную стоимость смены (по длительности)."""
        if not self.start_time or not self.end_time:
            return None

        duration = self.end_time - self.start_time
        hours = duration.total_seconds() / 3600
        return round(self.price * hours, 2)

    def __repr__(self):
        """Возвращает строковое представление объекта Exchange."""
        return (
            f"<Exchange {self.id} intent={self.owner_intent} owner={self.owner_id} "
            f"counterpart={self.counterpart_id} status={self.status} "
            f"start_time={self.start_time} price={self.price}>"
        )


class ExchangeSubscription(Base):
    """Расширенная модель подписки на новые обмены.

    Позволяет пользователям создавать гибкие подписки с различными фильтрами.

    Args:
        id: Уникальный идентификатор подписки
        subscriber_id: Идентификатор подписчика (внешний ключ на employees.user_id)
        name: Название подписки (пользователь может дать имя)
        exchange_type: Тип обменов для подписки (buy, sell, both)
        subscription_type: Тип подписки (all, price_range, date_range, time_range, seller_specific)
        min_price: Минимальная цена (включительно)
        max_price: Максимальная цена (включительно)
        start_date: Начальная дата диапазона
        end_date: Конечная дата диапазона
        start_time: Начальное время дня
        end_time: Конечное время дня
        days_of_week: Дни недели в формате JSON массива
        target_seller_id: Конкретный продавец
        is_active: Активна ли подписка
        created_at: Время создания подписки
        updated_at: Время последнего обновления

    Relationships:
        subscriber: Объект Employee подписчика
        target_seller: Объект Employee целевого продавца

    Indexes:
        idx_subscriber_active: (subscriber_id, is_active)
        idx_subscription_type_active: (subscription_type, is_active)
        idx_exchange_type_active: (exchange_type, is_active)
        idx_price_range: (min_price, max_price, is_active)
        idx_date_range: (start_date, end_date, is_active)
        idx_target_seller: (target_seller_id, is_active)
    """

    __tablename__ = "exchange_subscriptions"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор подписки",
    )
    subscriber_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="Идентификатор подписчика (employees.user_id)",
    )

    # Subscription metadata
    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Название подписки (пользователь может дать имя)",
    )
    exchange_type: Mapped[str] = mapped_column(
        Enum("buy", "sell", "both"),
        nullable=False,
        default="buy",
        comment="Тип обменов для подписки",
    )
    subscription_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="all",
        comment="Тип подписки (all, price_range, date_range, time_range, seller_specific)",
    )

    # Price filtering
    min_price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Минимальная цена (включительно)",
    )
    max_price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Максимальная цена (включительно)",
    )

    # Date/time filtering
    start_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
        comment="Начальная дата диапазона",
    )
    end_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
        comment="Конечная дата диапазона",
    )
    start_time: Mapped[time | None] = mapped_column(
        TIME,
        nullable=True,
        comment="Начальное время дня (например, 08:00)",
    )
    end_time: Mapped[time | None] = mapped_column(
        TIME,
        nullable=True,
        comment="Конечное время дня (например, 20:00)",
    )

    # Days of week filtering (JSON array)
    days_of_week: Mapped[list | None] = mapped_column(
        UnicodeJSON,
        nullable=True,
        comment="Дни недели [1,2,3,4,5] для пн-пт, null для всех",
    )

    # Seller filtering
    target_seller_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Конкретный продавец (employees.user_id)",
    )

    # Status and metadata
    is_active: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=True,
        comment="Активна ли подписка",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Время создания подписки",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="Время последнего обновления",
    )

    # Отношения
    subscriber: Mapped["Employee"] = relationship(
        "Employee",
        primaryjoin="foreign(ExchangeSubscription.subscriber_id) == Employee.user_id",
        back_populates="exchange_subscriptions",
        lazy="joined",
    )
    target_seller: Mapped["Employee"] = relationship(
        "Employee",
        primaryjoin="foreign(ExchangeSubscription.target_seller_id) == Employee.user_id",
        back_populates="target_subscriptions",
        lazy="select",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_subscriber_active", "subscriber_id", "is_active"),
        Index("idx_subscription_type_active", "subscription_type", "is_active"),
        Index("idx_exchange_type_active", "exchange_type", "is_active"),
        Index("idx_price_range", "min_price", "max_price", "is_active"),
        Index("idx_date_range", "start_date", "end_date", "is_active"),
        Index("idx_target_seller", "target_seller_id", "is_active"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта ExchangeSubscription."""
        return (
            f"<ExchangeSubscription {self.id} subscriber={self.subscriber_id} "
            f"name='{self.name}' type={self.subscription_type} active={self.is_active}>"
        )
