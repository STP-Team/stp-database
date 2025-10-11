"""Репозиторий для работы с моделями БД KPI."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.models.KPI.spec_kpi import SpecDayKPI, SpecMonthKPI, SpecWeekKPI
from stp_database.repo.KPI.head_premium import HeadPremiumRepo
from stp_database.repo.KPI.spec_kpi import SpecKPIRepo
from stp_database.repo.KPI.spec_premium import SpecPremiumRepo


@dataclass
class KPIRequestsRepo:
    """Репозиторий для обработки операций с БД. Этот класс содержит все репозитории для моделей базы данных KPI.

    Ты можешь добавить дополнительные репозитории в качестве свойств к этому классу, чтобы они были легко доступны.
    """

    session: AsyncSession

    @property
    def head_premium(self) -> HeadPremiumRepo:
        """Инициализация репозитория HeadPremiumRepo с сессией для работы с премией руководителей."""
        return HeadPremiumRepo(self.session)

    @property
    def spec_premium(self) -> SpecPremiumRepo:
        """Инициализация репозитория SpecPremiumRepo с сессией для работы с премией специалистов."""
        return SpecPremiumRepo(self.session)

    @property
    def spec_day_kpi(self) -> SpecKPIRepo:
        """Инициализация репозитория SpecKPIRepo с сессией для работы с дневными показателями специалистов."""
        return SpecKPIRepo(self.session, SpecDayKPI)

    @property
    def spec_week_kpi(self) -> SpecKPIRepo:
        """Инициализация репозитория SpecKPIRepo с сессией для работы с недельными показателями специалистов."""
        return SpecKPIRepo(self.session, SpecWeekKPI)

    @property
    def spec_month_kpi(self) -> SpecKPIRepo:
        """Инициализация репозитория SpecKPIRepo с сессией для работы с месячными показателями специалистов."""
        return SpecKPIRepo(self.session, SpecMonthKPI)
