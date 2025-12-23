"""Инициализация моделей Stats."""

from .head_premium import HeadPremium
from .sl import SL
from .spec_kpi import SpecDayKPI, SpecMonthKPI, SpecWeekKPI
from .spec_premium import SpecPremium
from .tests import AssignedTest
from .tutors_schedule import TutorsSchedule

__all__ = [
    "HeadPremium",
    "SpecDayKPI",
    "SpecMonthKPI",
    "SpecWeekKPI",
    "SpecPremium",
    "SL",
    "AssignedTest",
    "TutorsSchedule",
]
