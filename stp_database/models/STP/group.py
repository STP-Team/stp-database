"""Модели, связанные с сущностями групп."""

from sqlalchemy import JSON, Boolean, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Group(Base):
    """Класс, представляющий сущность группы в БД.

    Args:
        group_id: Идентификатор группы Telegram
        group_type: Тип группы
        invited_by: Идентификатор Telegram пригласившего
        remove_unemployed: Удалять уволенных сотрудников из группы
        is_casino_allowed: Разрешено ли использование команд казино в группе
        new_user_notify: Уведомлять ли о новых пользователях в группе
        allowed_roles: Список разрешенных ролей для доступа к группе
        service_messages: Список сервисных сообщений на удаление

    Methods:
        __repr__(): Возвращает строковое представление объекта Group.
    """

    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, comment="Идентификатор группы Telegram"
    )
    group_type: Mapped[str] = mapped_column(
        Enum("group", "channel"),
        nullable=False,
        comment="Тип группы: группа или канал",
        default="group",
    )
    invited_by: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор Telegram пригласившего"
    )
    remove_unemployed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Удалять уволенных сотрудников из группы",
        default=0,
    )
    is_casino_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Разрешено ли использование команд казино в группе",
        default=1,
    )
    new_user_notify: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Уведомлять ли о новых пользователях в группе",
        default=1,
    )
    allowed_roles: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment="Список разрешенных ролей для доступа к группе",
        default=[],
    )
    service_messages: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment="Список сервисных сообщений на удаление",
        default=[],
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Group."""
        return f"<Group {self.group_id} {self.invited_by} {self.remove_unemployed} {self.is_casino_allowed} {self.new_user_notify} {self.allowed_roles} {self.service_messages}>"
