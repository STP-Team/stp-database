"""Управление БД СТП."""

__version__ = "1.3.4"

# Конфигурация и настройка
from stp_database.config import DbConfig

# Модели
from stp_database.models import (
    Achievement,
    Broadcast,
    Employee,
    File,
    Group,
    GroupMember,
    HeadPremium,
    Product,
    Purchase,
    SpecKPI,
    SpecPremium,
    Transaction,
)

# Базовые классы
from stp_database.models.base import Base, TableNameMixin, TimestampMixin, int_pk
from stp_database.repo.base import BaseRepo

# Репозитории KPI
from stp_database.repo.KPI.head_premium import HeadPremiumRepo

# Основные репозитории запросов
from stp_database.repo.KPI.requests import KPIRequestsRepo
from stp_database.repo.KPI.spec_kpi import SpecKPIRepo
from stp_database.repo.KPI.spec_premium import SpecPremiumRepo

# Репозитории STP
from stp_database.repo.STP.achievement import AchievementsRepo
from stp_database.repo.STP.broadcast import BroadcastRepo
from stp_database.repo.STP.employee import EmployeeRepo
from stp_database.repo.STP.files import FilesRepo
from stp_database.repo.STP.group import GroupRepo
from stp_database.repo.STP.group_member import GroupMemberRepo
from stp_database.repo.STP.product import ProductsRepo
from stp_database.repo.STP.purchase import PurchaseRepo
from stp_database.repo.STP.requests import MainRequestsRepo
from stp_database.repo.STP.transactions import TransactionRepo
from stp_database.setup import create_engine, create_session_pool

__all__ = [
    # Версия
    "__version__",
    # Конфигурация и настройка
    "DbConfig",
    "create_engine",
    "create_session_pool",
    # Базовые классы и утилиты
    "Base",
    "BaseRepo",
    "TableNameMixin",
    "TimestampMixin",
    "int_pk",
    # Модели STP
    "Achievement",
    "Broadcast",
    "Employee",
    "Group",
    "GroupMember",
    "Product",
    "Purchase",
    "File",
    "Transaction",
    # Модели KPI
    "HeadPremium",
    "SpecKPI",
    "SpecPremium",
    # Основные репозитории запросов
    "KPIRequestsRepo",
    "MainRequestsRepo",
    # Репозитории STP
    "AchievementsRepo",
    "BroadcastRepo",
    "EmployeeRepo",
    "GroupRepo",
    "GroupMemberRepo",
    "ProductsRepo",
    "PurchaseRepo",
    "FilesRepo",
    "TransactionRepo",
    # Репозитории KPI
    "HeadPremiumRepo",
    "SpecKPIRepo",
    "SpecPremiumRepo",
]
