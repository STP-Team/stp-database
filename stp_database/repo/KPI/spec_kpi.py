"""Репозиторий для работы с KPI специалистов."""

import logging
from typing import Generic, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.KPI.spec_kpi import SpecKPI
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SpecKPI)


class SpecKPIRepo(BaseRepo, Generic[T]):
    """Универсальный репозиторий для работы с KPI специалистов.

    Работает с любой таблицей KPI (KpiDay, KpiWeek, KpiMonth) через один интерфейс.

    Attributes:
        model: Класс модели KPI (SpecDayKPI, SpecWeekKPI или SpecMonthKPI)
    """

    def __init__(self, session, model: Type[T]):
        """Инициализация репозитория.

        Args:
            session: Сессия SQLAlchemy
            model: Класс модели KPI (SpecDayKPI/SpecWeekKPI/SpecMonthKPI)
        """
        super().__init__(session)
        self.model = model

    async def get_kpi(self, fullnames: str | list[str]) -> T | None | Sequence[T]:
        """Поиск показателей специалистов в БД по ФИО.

        Args:
            fullnames: ФИО специалиста или список ФИО специалистов в БД

        Returns:
            Показатели KPI специалиста или None (если передана строка)
            Последовательность объектов SpecKPI (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        is_single = isinstance(fullnames, str)

        if is_single:
            query = select(self.model).where(self.model.fullname == fullnames)
        else:
            if not fullnames:
                return []
            query = select(self.model).where(self.model.fullname.in_(fullnames))

        try:
            result = await self.session.execute(query)
            if is_single:
                return result.scalar_one_or_none()
            else:
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения показателей специалиста(-ов) из {self.model.__tablename__}: {e}"
            )
            return None if is_single else []
