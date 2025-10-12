"""Модели, связанные с сущностями пользователей."""

from datetime import datetime

from sqlalchemy import BIGINT, BOOLEAN, DateTime, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class User(Base):
    """Модель, представляющий сущность пользователя в БД.

    Args:
        id: Уникальный идентификатор пользователя
        user_id: Идентификатор пользователя в Telegram
        username: Username пользователя в Telegram
        fullname: ФИО пользователя
        is_admin: Является ли пользователь администратором
        paid: Сумма оплаты пользователя
        token: Токен пользователя
        birth_date: Дата рождения пользователя
        verified: Верифицирован ли пользователь
        notify_all: Уведомления для всех
        gathering: Участие в сборе
        need_pay: Необходимая сумма к оплате
        status: Статус пользователя
        group_name: Название группы пользователя
        curator: Является ли пользователь куратором
        group_id: Идентификатор группы
        ignore: Игнорировать пользователя

    Methods:
        __repr__(): Возвращает строковое представление объекта User.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Уникальный идентификатор пользователя",
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор пользователя в Telegram",
        name="tgid",
    )
    username: Mapped[str] = mapped_column(
        Unicode(250), nullable=True, comment="Username пользователя в Telegram"
    )
    fullname: Mapped[str] = mapped_column(
        Unicode(250), nullable=True, comment="ФИО пользователя", name="FIO"
    )
    is_admin: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=True,
        comment="Является ли пользователь администратором",
        name="IsAdmin",
    )
    paid: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Сумма оплаты пользователя"
    )
    token: Mapped[str] = mapped_column(
        Unicode(500), nullable=True, comment="Токен пользователя"
    )
    birth_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="Дата рождения пользователя"
    )
    verified: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Верифицирован ли пользователь"
    )
    notify_all: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Уведомления для всех", name="notif_4_all"
    )
    gathering: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Участие в сборе", name="sbor"
    )
    need_pay: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Необходимая сумма к оплате"
    )
    status: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Статус пользователя"
    )
    group_name: Mapped[str] = mapped_column(
        Unicode(500), nullable=True, comment="Название группы пользователя"
    )
    curator: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Является ли пользователь куратором"
    )
    group_id: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Идентификатор группы",
        name="group_identificator",
    )
    ignore: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Игнорировать пользователя"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта User."""
        return f"<User {self.id} {self.user_id} {self.username} {self.fullname}>"
