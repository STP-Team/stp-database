"""Модели, связанные с сущностями участников групп."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column


class GroupMember:
    """Класс, представляющий сущность участника группы в БД.

    Args:
        group_id: Идентификатор Telegram группы
        member_id: Идентификатор Telegram вступившего участника
        added_at: Время вступления участника в группу

    Methods:
        __repr__(): Возвращает строковое представление объекта GroupMember.
    """

    __tablename__ = "group_members"

    group_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("groups.group_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор Telegram группы",
    )
    member_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, comment="Идентификатор Telegram вступившего участника"
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Время вступления участника в группу",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта GroupMember."""
        return f"<GroupMember {self.group_id} {self.member_id} {self.added_at}>"
