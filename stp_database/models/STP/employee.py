"""Модели, связанные с сущностями сотрудников."""

from typing import TYPE_CHECKING

from sqlalchemy import BIGINT, BOOLEAN, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stp_database.models.base import Base

if TYPE_CHECKING:
    from stp_database.models.STP.event_log import EventLog
    from stp_database.models.STP.exchange import Exchange, ExchangeSubscription


class Employee(Base):
    """Модель, представляющий сущность сотрудника в БД.

    Args:
        id: Уникальный идентификатор пользователя
        user_id: Идентификатор сотрудника в Telegram
        username: Username сотрудника в Telegram
        division: Направление сотрудника (НТП/НЦК)
        position: Позиция/должность сотрудника
        fullname: ФИО сотрудника
        head: ФИО руководителя сотрудника
        email: Email сотрудника
        role: Уровень доступа сотрудника в БД
        is_trainee: Является ли сотрудник стажером
        is_casino_allowed: Разрешено ли казино сотруднику
        is_exchange_banned: Забанен ли сотрудник на бирже смен

    Methods:
        __repr__(): Возвращает строковое представление объекта Employee.
    """

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, comment="Уникальный идентификатор пользователя"
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT, nullable=True, comment="Идентификатор сотрудника в Telegram"
    )
    username: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Username сотрудника в Telegram"
    )
    division: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Направление сотрудника (НТП/НЦК)"
    )
    position: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Позиция/должность сотрудника"
    )
    fullname: Mapped[str] = mapped_column(
        Unicode, nullable=False, comment="ФИО сотрудника"
    )
    head: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="ФИО руководителя сотрудника"
    )
    email: Mapped[str] = mapped_column(
        Unicode, nullable=True, comment="Email сотрудника"
    )
    role: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Уровень доступа сотрудника в БД"
    )
    is_trainee: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, default=True, comment="Является ли сотрудник стажером"
    )
    is_casino_allowed: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, comment="Разрешено ли казино сотруднику"
    )
    is_exchange_banned: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        comment="Забанен ли сотрудник на бирже подмен",
    )

    # Отношения
    event_logs: Mapped[list["EventLog"]] = relationship(
        "EventLog", back_populates="employee", lazy="select"
    )
    sold_exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.seller_id",
        back_populates="seller",
        lazy="select",
    )
    bought_exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.buyer_id",
        back_populates="buyer",
        lazy="select",
    )
    exchange_subscriptions: Mapped[list["ExchangeSubscription"]] = relationship(
        "ExchangeSubscription",
        foreign_keys="ExchangeSubscription.subscriber_id",
        back_populates="subscriber",
        lazy="select",
    )
    target_subscriptions: Mapped[list["ExchangeSubscription"]] = relationship(
        "ExchangeSubscription",
        foreign_keys="ExchangeSubscription.target_seller_id",
        back_populates="target_seller",
        lazy="select",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Employee."""
        return f"<Employee {self.id} {self.user_id} {self.username} {self.fullname} {self.head} {self.email} {self.role}>"
