import logging
from typing import Generic, Optional, Sequence, Type, TypeVar

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

    async def get_kpi(self, fullname: str) -> Optional[T]:
        """Поиск показателей специалиста в БД по ФИО.

        Args:
            fullname: ФИО специалиста в БД

        Returns:
            Показатели KPI специалиста или None
        """
        query = select(self.model).where(self.model.fullname == fullname)

        try:
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения показателей специалиста из {self.model.__tablename__}: {e}"
            )
            return None

    async def get_kpi_by_names(self, fullnames: list[str]) -> Sequence[T]:
        """Поиск показателей специалистов в БД по списку ФИО.

        Args:
            fullnames: Список ФИО специалистов в БД

        Returns:
            Последовательность объектов SpecKPI
        """
        if not fullnames:
            return []

        query = select(self.model).where(self.model.fullname.in_(fullnames))

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения показателей специалистов из {self.model.__tablename__}: {e}"
            )
            return []
