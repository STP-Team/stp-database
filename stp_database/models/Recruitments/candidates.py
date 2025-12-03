"""Модели, связанные с сущностями кандидатов."""

from typing import Optional

from sqlalchemy import BIGINT, Enum, Integer
from sqlalchemy.dialects.mysql import LONGTEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Candidate(Base):
    """Класс, представляющий сущность кандидата в БД.

    Args:
        user_id: Уникальный идентификатор Telegram кандидата
        fullname: ФИО кандидата
        position: Название позиции, на которую подается кандидат
        age: Возраст кандидата
        topic_id: Идентификатор Telegram топика, которому принадлежит кандидат
        status: Статус кандидата
        city: Город кандидата
        username: Имя пользователя Telegram кандидата
        phone_number: Номер телефона кандидата
        shift_type: Тип смены (полная/частичная)
        shift_time: Время смены (день/ночь/любое)
        experience: Опыт работы
        workplace: Рабочее место кандидата
        internet_speed: Скорость интернета кандидата
        typing_speed: Скорость печати кандидата
        resume_link: Ссылка на резюме кандидата

    Methods:
        __repr__(): Возвращает строковое представление объекта Candidate.
    """

    __tablename__ = "candidates"

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        nullable=False,
        comment="Идентификатор Telegram кандидата",
    )
    fullname: Mapped[Optional[str]] = mapped_column(
        VARCHAR(255), nullable=True, comment="ФИО кандидата"
    )
    position: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="Название позиции, на которую подается кандидат",
    )
    age: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Возраст кандидата"
    )
    topic_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        nullable=True,
        comment="Идентификатор Telegram топика, которому принадлежит кандидат",
    )
    status: Mapped[str] = mapped_column(
        Enum("interview", "waiting", "review", "decline", "accept"),
        nullable=False,
        comment="Статус кандидата",
        default="interview",
    )
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    shift_type: Mapped[Optional[str]] = mapped_column(
        Enum("full", "part"), nullable=True
    )
    shift_time: Mapped[Optional[str]] = mapped_column(
        Enum("day", "night", "any"), nullable=True
    )
    experience: Mapped[Optional[str]] = mapped_column(
        Enum("chats", "calls", "in-person", "no"), nullable=True
    )
    workplace: Mapped[Optional[str]] = mapped_column(
        LONGTEXT, nullable=True, comment="Рабочее место кандидата"
    )
    internet_speed: Mapped[Optional[str]] = mapped_column(
        Enum("<20", "50<>20", "100<>50", ">100"),
        nullable=True,
        comment="Скорость интернета кандидата",
    )
    typing_speed: Mapped[Optional[str]] = mapped_column(
        VARCHAR(255), nullable=True, comment="Скорость печати кандидата"
    )
    resume_link: Mapped[Optional[str]] = mapped_column(
        VARCHAR(255), nullable=True, comment="Ссылка на резюме кандидата"
    )
    manager_user_id: Mapped[Optional[int]] = mapped_column(
        BIGINT, nullable=True, comment="Менеджер, принявший решение по кандидату"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Candidate."""
        return f"<Candidate {self.user_id} {self.position} {self.status}>"
