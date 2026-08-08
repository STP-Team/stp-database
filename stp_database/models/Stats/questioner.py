from datetime import datetime
import uuid

from sqlalchemy import Integer, text, Float, BIGINT, DateTime, Enum, Unicode, func, Text
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from stp_database import Base



def generate_uuid() -> str:
    return str(uuid.uuid4())


class QuestionerChats(Base):
    """Ежедневная статистика закрытых чатов вопросника."""

    __tablename__ = "QuestionerChats"

    uuid: Mapped[str] = mapped_column(
        Unicode(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=generate_uuid,
        comment="Уникальный идентификатор записи",
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="ID пользователя из employees.id",
    )

    chat_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        comment="ID чата из локальной БД вопросника",
    )

    role_user: Mapped[str] = mapped_column(
        Enum(
            "requester",
            "responser",
            "other",
            name="questioner_role_user",
        ),
        nullable=False,
        comment="Роль пользователя в чате",
    )

    kb_link: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Ссылка на БЗ",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата создания чата",
    )

    closed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата закрытия чата",
    )

    rate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Оценка участника чата",
    )

    logged_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Дата занесения статистики",
    )

    def __repr__(self) -> str:
        return (
            f"<QuestionerChats "
            f"uuid={self.uuid} "
            f"user_id={self.user_id} "
            f"chat_id={self.chat_id} "
            f"role_user={self.role_user}>"
        )


class QuestionerMonth(Base):
    """Статистика с вопросника за месяц."""

    __tablename__ = "QuestionerMonth"

    employee_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Идентификатор сотрудника",
    )

    count_questions_asked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Количество заданных вопросов",
    )

    count_questions_answered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Количество отвеченных вопросов",
    )

    average_duration_asked_question: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default=text("0"),
        comment="Средняя продолжительность заданного вопроса",
    )

    average_duration_answered_question: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default=text("0"),
        comment="Средняя продолжительность отвеченного вопроса",
    )

    rate_requester: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Оценка задающего вопрос",
    )

    rate_responder: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Оценка отвечающего на вопрос"
    )

    extraction_period: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        comment="Месяц, за который рассчитана статистика",
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Дата последнего обновления статистики"
    )

    def __repr__(self) -> str:
        return (
            f"<QuestionerMonth "
            f"employee_id={self.employee_id} "
            f"asked={self.count_questions_asked} "
            f"answered={self.count_questions_answered} "
        )