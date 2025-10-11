from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.models.KPI.spec_kpi import SpecDayKPI, SpecMonthKPI, SpecWeekKPI
from stp_database.repo.KPI.head_premium import HeadPremiumRepo
from stp_database.repo.KPI.spec_kpi import SpecKPIRepo
from stp_database.repo.KPI.spec_premium import SpecPremiumRepo


@dataclass
class KPIRequestsRepo:
    """Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def head_premium(self) -> HeadPremiumRepo:
        """The HeadPremiumRepo repository sessions are required to manage head premium operations."""
        return HeadPremiumRepo(self.session)

    @property
    def spec_day_kpi(self) -> SpecKPIRepo:
        """The SpecKPIRepo repository sessions are required to manage specialist daily kpi operations."""
        return SpecKPIRepo(self.session, SpecDayKPI)

    @property
    def spec_week_kpi(self) -> SpecKPIRepo:
        """The SpecKPIRepo repository sessions are required to manage specialist weekly kpi operations."""
        return SpecKPIRepo(self.session, SpecWeekKPI)

    @property
    def spec_month_kpi(self) -> SpecKPIRepo:
        """The SpecKPIRepo repository sessions are required to manage specialist monthly kpi operations."""
        return SpecKPIRepo(self.session, SpecMonthKPI)

    @property
    def spec_premium(self) -> SpecPremiumRepo:
        """The SpecPremiumRepo repository sessions are required to manage specialist premium operations."""
        return SpecPremiumRepo(self.session)
