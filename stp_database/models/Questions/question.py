"""Модели, связанные с сущностями вопросов."""

from datetime import datetime

from sqlalchemy import BIGINT, BOOLEAN, DateTime, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Question(Base):
    """Модель, представляющая сущность вопроса в БД.

    Args:
        token: Уникальный токен вопроса (первичный ключ)
        group_id: Идентификатор Telegram группы
        topic_id: Идентификатор Telegram темы в группе
        duty_userid: Идентификатор Telegram дежурного
        employee_userid: Идентификатор Telegram сотрудника
        question_text: Текст вопроса
        start_time: Время начала
        end_time: Время окончания
        clever_link: Ссылка на Clever
        quality_duty: Оценка качества дежурного
        quality_employee: Оценка качества сотрудника
        status: Статус вопроса
        allow_return: Разрешен ли возврат
        activity_status_enabled: Включен ли статус активности

    Methods:
        __repr__(): Возвращает строковое представление объекта Question.
    """

    __tablename__ = "questions"

    token: Mapped[str] = mapped_column(
        Unicode(255),
        primary_key=True,
        comment="Уникальный токен вопроса",
    )
    group_id: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор Telegram группы"
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Идентификатор Telegram темы в группе"
    )
    employee_topic_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Идентификатор Telegram темы сотрудника"
    )
    duty_userid: Mapped[int] = mapped_column(
        BIGINT, nullable=True, comment="Идентификатор Telegram дежурного"
    )
    employee_userid: Mapped[int] = mapped_column(
        BIGINT, nullable=False, comment="Идентификатор Telegram сотрудника"
    )
    question_text: Mapped[str] = mapped_column(
        Unicode(5000), nullable=True, comment="Текст вопроса"
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="Время начала"
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="Время окончания"
    )
    clever_link: Mapped[str] = mapped_column(
        Unicode(5000), nullable=True, comment="Ссылка на Clever"
    )
    quality_duty: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Оценка качества дежурного"
    )
    quality_employee: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Оценка качества сотрудника"
    )
    status: Mapped[str] = mapped_column(
        Unicode(5000), nullable=True, comment="Статус вопроса"
    )
    allow_return: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, comment="Разрешен ли возврат"
    )
    activity_status_enabled: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=True, comment="Включен ли статус активности"
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Question."""
        return f"<Question {self.token} {self.group_id} {self.topic_id} {self.status}>"
