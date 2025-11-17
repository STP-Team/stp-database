"""Модели, связанные с сущностями кандидатов."""

from sqlalchemy import BIGINT, Enum
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Candidate(Base):
    """Класс, представляющий сущность кандидата в БД.

    Args:
        user_id: Уникальный идентификатор Telegram кандидата
        fullname: ФИО кандидата
        position: Позиция, на которую подается кандидат
        status: Статус отклика

    Methods:
        __repr__(): Возвращает строковое представление объекта Candidate.
    """

    __tablename__ = "candidates"

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        nullable=False,
        comment="Уникальный идентификатор Telegram кандидата",
    )
    fullname: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО кандидата"
    )
    position: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, comment="Позиция, на которую подается кандидат"
    )
    status: Mapped[str] = mapped_column(
        Enum("interview", "review", "decline", "accept"),
        nullable=False,
        comment="Статус отклика",
        default="interview",
    )
    topic_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор Telegram топика, которому принадлежит кандидат",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Candidate."""
        return f"<Candidate {self.user_id} {self.position} {self.status}>"
