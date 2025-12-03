"""Инициализация моделей KPI."""

from .head_premium import HeadPremium
from .spec_kpi import SpecDayKPI, SpecMonthKPI, SpecWeekKPI
from .spec_premium import SpecPremium

__all__ = ["HeadPremium", "SpecDayKPI", "SpecMonthKPI", "SpecWeekKPI", "SpecPremium"]
