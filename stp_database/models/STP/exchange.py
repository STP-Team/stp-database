"""Модели для системы сделки сменами (биржи смен)."""

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    DATE,
    JSON,
    TIME,
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
        start_time: Начало смены
        end_time: Окончание смены (если частичная смена)
        price: Цена за смену или часть смены
        comment: Комментарий к сделке
        type: Тип обмена (sell, buy)
        status: Статус сделки (active, sold, cancelled)
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
        idx_start_time: (start_time)
        idx_created_at: (created_at)
        idx_status_start_time: (status, start_time)
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
    seller_id: Mapped[int | None] = mapped_column(
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
    type: Mapped[str] = mapped_column(
        Enum("sell", "buy"),
        nullable=False,
        default="sell",
        comment="Тип обмена: sell - предложение продать смену, buy - запрос на покупку смены",
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
    in_seller_schedule: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Показывать ли в графике продающего",
    )
    in_buyer_schedule: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Показывать ли в графике покупающего",
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
    # Note: Subscriptions are no longer directly linked to specific exchanges
    # They use filtering logic instead

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_seller_id", "seller_id"),
        Index("idx_buyer_id", "buyer_id"),
        Index("idx_status", "status"),
        Index("idx_start_time", "start_time"),
        Index("idx_created_at", "created_at"),
        Index("idx_status_start_time", "status", "start_time"),
        Index("idx_seller_status", "seller_id", "status"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Exchange."""
        return (
            f"<Exchange {self.id} type={self.type} seller={self.seller_id} "
            f"buyer={self.buyer_id} status={self.status} "
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
        target_divisions: Подразделения в формате JSON массива
        notify_immediately: Уведомлять сразу при появлении подходящего обмена
        notify_daily_digest: Отправлять ежедневную сводку
        notify_before_expire: Уведомлять перед истечением подходящих обменов
        digest_time: Время отправки дневной сводки
        is_active: Активна ли подписка
        created_at: Время создания подписки
        updated_at: Время последнего обновления
        last_notified_at: Время последнего уведомления
        last_digest_at: Время последней дневной сводки
        notifications_sent: Количество отправленных уведомлений
        matches_found: Количество найденных совпадений

    Relationships:
        subscriber: Объект Employee подписчика
        target_seller: Объект Employee целевого продавца
        notifications: История уведомлений

    Indexes:
        idx_subscriber_active: (subscriber_id, is_active)
        idx_subscription_type_active: (subscription_type, is_active)
        idx_exchange_type_active: (exchange_type, is_active)
        idx_price_range: (min_price, max_price, is_active)
        idx_date_range: (start_date, end_date, is_active)
        idx_target_seller: (target_seller_id, is_active)
        idx_notifications: (notify_immediately, is_active)
        idx_digest_schedule: (notify_daily_digest, digest_time, is_active)
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
        ForeignKey(
            "employees.user_id",
            name="fk_subscriptions_subscriber",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="Идентификатор подписчика (внешний ключ на employees.user_id)",
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
        JSON,
        nullable=True,
        comment="Дни недели [1,2,3,4,5] для пн-пт, null для всех",
    )

    # Seller filtering
    target_seller_id: Mapped[int | None] = mapped_column(
        BIGINT,
        ForeignKey(
            "employees.user_id",
            name="fk_subscriptions_target_seller",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
        comment="Конкретный продавец (для подписки на конкретного человека)",
    )

    # Division filtering
    target_divisions: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        comment='Подразделения ["НЦК", "НТП1"] для фильтрации',
    )

    # Notification settings
    notify_immediately: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=True,
        comment="Уведомлять сразу при появлении подходящего обмена",
    )
    notify_daily_digest: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Отправлять ежедневную сводку",
    )
    notify_before_expire: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Уведомлять перед истечением подходящих обменов",
    )
    digest_time: Mapped[time] = mapped_column(
        TIME,
        nullable=False,
        default=time(9, 0),
        comment="Время отправки дневной сводки",
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
    last_notified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Время последнего уведомления",
    )
    last_digest_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        comment="Время последней дневной сводки",
    )

    # Statistics
    notifications_sent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Количество отправленных уведомлений",
    )
    matches_found: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Количество найденных совпадений",
    )

    # Отношения
    subscriber: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[subscriber_id],
        back_populates="exchange_subscriptions",
        lazy="joined",
    )
    target_seller: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[target_seller_id],
        lazy="select",
    )
    notifications: Mapped[list["SubscriptionNotification"]] = relationship(
        "SubscriptionNotification",
        back_populates="subscription",
        lazy="select",
        cascade="all, delete-orphan",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_subscriber_active", "subscriber_id", "is_active"),
        Index("idx_subscription_type_active", "subscription_type", "is_active"),
        Index("idx_exchange_type_active", "exchange_type", "is_active"),
        Index("idx_price_range", "min_price", "max_price", "is_active"),
        Index("idx_date_range", "start_date", "end_date", "is_active"),
        Index("idx_target_seller", "target_seller_id", "is_active"),
        Index("idx_notifications", "notify_immediately", "is_active"),
        Index("idx_digest_schedule", "notify_daily_digest", "digest_time", "is_active"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта ExchangeSubscription."""
        return (
            f"<ExchangeSubscription {self.id} subscriber={self.subscriber_id} "
            f"name='{self.name}' type={self.subscription_type} active={self.is_active}>"
        )


class SubscriptionNotification(Base):
    """Модель истории уведомлений по подпискам.

    Хранит информацию о всех отправленных уведомлениях.

    Args:
        id: Уникальный идентификатор уведомления
        subscription_id: Идентификатор подписки
        exchange_id: Идентификатор сделки
        notification_type: Тип уведомления (immediate, digest, expiry)
        sent_at: Время отправки уведомления

    Relationships:
        subscription: Объект ExchangeSubscription
        exchange: Объект Exchange

    Indexes:
        idx_subscription_notifications: (subscription_id, sent_at)
        idx_exchange_notifications: (exchange_id, notification_type)
        idx_sent_at: (sent_at)
    """

    __tablename__ = "subscription_notifications"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор уведомления",
    )
    subscription_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "exchange_subscriptions.id",
            name="fk_notifications_subscription",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="Идентификатор подписки",
    )
    exchange_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "exchanges.id",
            name="fk_notifications_exchange",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="Идентификатор сделки",
    )
    notification_type: Mapped[str] = mapped_column(
        Enum("immediate", "digest", "expiry"),
        nullable=False,
        comment="Тип уведомления",
    )
    sent_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Время отправки уведомления",
    )

    # Отношения
    subscription: Mapped["ExchangeSubscription"] = relationship(
        "ExchangeSubscription",
        foreign_keys=[subscription_id],
        back_populates="notifications",
        lazy="select",
    )
    exchange: Mapped["Exchange"] = relationship(
        "Exchange",
        foreign_keys=[exchange_id],
        lazy="select",
    )

    # Индексы и настройки таблицы
    __table_args__ = (
        Index("idx_subscription_notifications", "subscription_id", "sent_at"),
        Index("idx_exchange_notifications", "exchange_id", "notification_type"),
        Index("idx_sent_at", "sent_at"),
        {"mysql_collate": "utf8mb4_unicode_ci"},
    )

    def __repr__(self):
        """Возвращает строковое представление объекта SubscriptionNotification."""
        return (
            f"<SubscriptionNotification {self.id} subscription={self.subscription_id} "
            f"exchange={self.exchange_id} type={self.notification_type}>"
        )
