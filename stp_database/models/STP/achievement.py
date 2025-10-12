"""Модели, связанные с сущностями достижений."""

from sqlalchemy import Enum, Integer
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Achievement(Base):
    """Класс, представляющий сущность достижения в БД.

    Args:
        id: Уникальный идентификатор достижения
        name: Название достижения
        description: Описание достижения
        division: Направление сотрудника (НТП/НЦК) для получения достижения
        kpi: Показатели KPI для получения достижения
        reward: Награда за получение достижение в баллах
        position: Позиция/должность сотрудника для получения достижения
        period: Частота возможного получения достижения: день, неделя, месяц и ручная

    Methods:
        __repr__(): Возвращает строковое представление объекта Achievement.
    """

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор достижения",
    )
    name: Mapped[str] = mapped_column(
        VARCHAR(30), nullable=False, comment="Название достижения"
    )
    description: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, comment="Описание достижения"
    )
    division: Mapped[str] = mapped_column(
        VARCHAR(3),
        nullable=False,
        comment="Направление сотрудника (НТП/НЦК) для получения достижения",
    )
    kpi: Mapped[str] = mapped_column(
        VARCHAR(3), nullable=False, comment="Показатели KPI для получения достижения"
    )
    reward: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Награда за получение достижение в баллах"
    )
    position: Mapped[str] = mapped_column(
        VARCHAR(31),
        nullable=False,
        comment="Позиция/должность сотрудника для получения достижения",
    )
    period: Mapped[str] = mapped_column(
        Enum("d", "w", "m", "A"),
        nullable=False,
        comment="Частота возможного получения достижения: день, неделя, месяц и ручная",
    )

    def __repr__(self):
        """Возвращает строковое представление объекта Achievement."""
        return f"<Achievement {self.id} {self.name} {self.description} {self.division} {self.kpi} {self.reward} {self.position} {self.period}>"
