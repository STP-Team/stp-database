"""Модели для системы сделки сменами (биржи смен)."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    TIMESTAMP,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Unicode,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stp_database.models.base import Base

if TYPE_CHECKING:
    from stp_database.models.STP.employee import Employee


class Exchange(Base):
    """Модель сделки сменой или частью смены.

    Представляет объявление о продаже/обмене смены на бирже.

    Args:
        id: Уникальный идентификатор сделки
        seller_id: Идентификатор продавца (внешний ключ на employees.user_id)
        buyer_id: Идентификатор покупателя (внешний ключ на employees.user_id)
        shift_date: Дата смены
        shift_start_time: Время начала смены
        shift_end_time: Время окончания смены (для частичной смены)
        is_partial: Является ли сделка частичной сменой
        price: Цена за смену или часть смены
        description: Описание сделки
        status: Статус сделки (active, sold, hidden, cancelled)
        is_hidden: Скрыта ли подмена
        is_private: Является ли подмена приватной
        is_paid: Отметка о наличии оплаты
        payment_type: Тип оплаты (immediate, on_date)
        payment_date: Конкретная дата оплаты
        created_at: Время создания объявления
        updated_at: Время последнего обновления
        sold_at: Время продажи

    Relationships:
        seller: Объект Employee продавца
        buyer: Объект Employee покупателя
        subscriptions: Подписки на этот сделка

    Indexes:
        idx_seller_id: (seller_id)
        idx_buyer_id: (buyer_id)
        idx_status: (status)
        idx_shift_date: (shift_date)
        idx_created_at: (created_at)
        idx_status_date: (status, shift_date)
        idx_seller_status: (seller_id, status)
    """

    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор сделки",
    )

    # Участники сделки
    seller_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("employees.user_id", name="fk_exchanges_seller"),
        nullable=False,
        comment="Идентификатор продавца (внешний ключ на employees.user_id)",
    )
    buyer_id: Mapped[int | None] = mapped_column(
        BIGINT,
        ForeignKey("employees.user_id", name="fk_exchanges_buyer"),
        nullable=True,
        comment="Идентификатор покупателя (внешний ключ на employees.user_id)",
    )

    # Информация о смене
    shift_date: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        comment="Дата смены",
    )
    shift_start_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Время начала смены (например, '09:00')",
    )
    shift_end_time: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Время окончания смены (для частичной смены)",
    )
    is_partial: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Является ли сделка частичной сменой",
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

    # Статус и видимость
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", "sold", "canceled"),
        nullable=False,
        default="active",
        comment="Статус сделки (active, inactive, sold, canceled)",
    )
    is_hidden: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Скрыта ли подмена (для временного скрытия)",
    )
    is_private: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Является ли подмена приватной (для отправки в личные сообщения)",
    )

    # Дополнительная информация
    description: Mapped[str | None] = mapped_column(
        Unicode(500),
        nullable=True,
        comment="Описание сделки",
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
    seller: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[seller_id],
        back_populates="sold_exchanges",
        lazy="joined",
    )
    buyer: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[buyer_id],
        back_populates="bought_exchanges",
        lazy="joined",
    )
    subscriptions: Mapped[list["ExchangeSubscription"]] = relationship(
        "ExchangeSubscription",
        back_populates="exchange",
        lazy="select",
        cascade="all, delete-orphan",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_seller_id", "seller_id"),
        Index("idx_buyer_id", "buyer_id"),
        Index("idx_status", "status"),
        Index("idx_shift_date", "shift_date"),
        Index("idx_created_at", "created_at"),
        Index("idx_status_date", "status", "shift_date"),
        Index("idx_seller_status", "seller_id", "status"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Exchange."""
        return (
            f"<Exchange {self.id} seller={self.seller_id} "
            f"buyer={self.buyer_id} status={self.status} "
            f"date={self.shift_date} price={self.price}>"
        )


class ExchangeSubscription(Base):
    """Модель подписки на новые сделки.

    Позволяет пользователям подписываться на уведомления о новых сделких.

    Args:
        id: Уникальный идентификатор подписки
        subscriber_id: Идентификатор подписчика (внешний ключ на employees.user_id)
        exchange_id: Идентификатор сделки (внешний ключ на exchanges.id)
        subscription_type: Тип подписки (all, specific_date, specific_seller)
        shift_date: Дата смены (для подписки на конкретную дату)
        is_active: Активна ли подписка
        created_at: Время создания подписки
        notified_at: Время последнего уведомления

    Relationships:
        subscriber: Объект Employee подписчика
        exchange: Объект Exchange (если подписка на конкретный сделка)

    Indexes:
        idx_subscriber_id: (subscriber_id)
        idx_exchange_id: (exchange_id)
        idx_is_active: (is_active)
        idx_subscriber_active: (subscriber_id, is_active)
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
        ForeignKey("employees.user_id", name="fk_subscriptions_subscriber"),
        nullable=False,
        comment="Идентификатор подписчика (внешний ключ на employees.user_id)",
    )
    exchange_id: Mapped[int | None] = mapped_column(
        BIGINT,
        ForeignKey("exchanges.id", name="fk_subscriptions_exchange"),
        nullable=True,
        comment="Идентификатор сделки (для подписки на конкретный сделка)",
    )
    subscription_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="all",
        comment="Тип подписки (all, specific_date, specific_seller)",
    )
    shift_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Дата смены (для подписки на конкретную дату)",
    )
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
    notified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Время последнего уведомления",
    )

    # Отношения
    subscriber: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[subscriber_id],
        back_populates="exchange_subscriptions",
        lazy="joined",
    )
    exchange: Mapped["Exchange"] = relationship(
        "Exchange",
        foreign_keys=[exchange_id],
        back_populates="subscriptions",
        lazy="select",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_subscriber_id", "subscriber_id"),
        Index("idx_exchange_id", "exchange_id"),
        Index("idx_is_active", "is_active"),
        Index("idx_subscriber_active", "subscriber_id", "is_active"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта ExchangeSubscription."""
        return (
            f"<ExchangeSubscription {self.id} subscriber={self.subscriber_id} "
            f"type={self.subscription_type} active={self.is_active}>"
        )
