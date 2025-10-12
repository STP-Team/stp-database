"""Модели, связанные с сущностями покупок предметов."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Purchase(Base):
    """Класс, представляющий сущность покупки пользователя в БД.

    Args:
        id: Уникальный идентификатор покупки
        user_id: Идентификатор сотрудника в Telegram, купившего предмет
        product_id: Идентификатор предмета
        usage_count: Кол-во использований предмета
        bought_at: Время приобретения предмета
        user_comment: Комментарий специалиста к активации предмета
        manager_comment: Комментарий менеджера к активации предмета
        updated_at: Время подтверждения активации предмета
        updated_by_user_id: Идентификатор пользователя Telegram, изменившего статус активации предмета
        status: Статус предмета (хранение, ожидание активации, израсходован)

    Methods:
        __repr__(): Возвращает строковое представление объекта Purchase.
    """

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор покупки",
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор сотрудника в Telegram, купившего предмет",
    )
    product_id: Mapped[int] = mapped_column(
        VARCHAR(255), nullable=False, comment="Идентификатор предмета"
    )
    usage_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Кол-во использований предмета"
    )
    bought_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Время приобретения предмета"
    )
    user_comment: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=True,
        comment="Комментарий специалиста к активации предмета",
    )
    manager_comment: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=True,
        comment="Комментарий менеджера к активации предмета",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment="Время подтверждения активации предмета",
    )
    updated_by_user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор пользователя Telegram, изменившего статус активации предмета",
    )
    status: Mapped[str] = mapped_column(
        Enum("stored", "review", "used_up"),
        nullable=False,
        default="stored",
        comment="Статус предмета (хранение, ожидание активации, израсходован)",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Purchase."""
        return f"<ProductUsage {self.id} {self.user_id} {self.product_id} {self.usage_count} {self.bought_at} {self.updated_at} {self.updated_by_user_id} {self.status}>"
