"""Модели, связанные с сущностями достижений."""

from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column


class Achievement:
    """Класс, представляющий сущность достижения в БД.

    Args:
        id: Уникальный идентификатор достижения
        name: Название достижения
        description: Описание достижения
        division: Направление сотрудника (НТП/НЦК) для получения достижения
        kpi: Показатели KPI для получения достижения
        reward: Награда за получение достижение в баллах
        position: Позиция/должность сотрудника для получения достижения

    Methods:
        __repr__(): Возвращает строковое представление объекта Achievement.
    """

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    description: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    division: Mapped[str] = mapped_column(VARCHAR(3), nullable=False)
    kpi: Mapped[str] = mapped_column(VARCHAR(3), nullable=False)
    reward: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[str] = mapped_column(VARCHAR(31), nullable=False)
    period: Mapped[str] = mapped_column(VARCHAR(1), nullable=False)

    def __repr__(self):
        """Возвращает строковое представление объекта Achievement."""
        return f"<Achievement {self.id} {self.name} {self.description} {self.division} {self.kpi} {self.reward} {self.position} {self.period}>"
