"""Управление БД СТП."""

__version__ = "1.7.7"

# Конфигурация и настройка
from stp_database.config import DbConfig

# Модели STP
# Модели KPI
# Модели Gifter
# Модели Questioner
from stp_database.models import (
    Achievement,
    Broadcast,
    Employee,
    Event,
    EventLog,
    Exchange,
    ExchangeSubscription,
    File,
    Group,
    GroupMember,
    HeadPremium,
    MessagesPair,
    Product,
    Purchase,
    Question,
    Settings,
    SpecKPI,
    SpecPremium,
    Transaction,
    User,
    UserEvent,
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
from stp_database.repo.Questions.requests import QuestionsRequestsRepo

# Репозитории STP
from stp_database.repo.STP.achievement import AchievementsRepo
from stp_database.repo.STP.broadcast import BroadcastRepo
from stp_database.repo.STP.employee import EmployeeRepo
from stp_database.repo.STP.event_log import EventLogRepo
from stp_database.repo.STP.exchange import ExchangeRepo
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
    "File",
    "Group",
    "GroupMember",
    "Product",
    "Purchase",
    "Transaction",
    # Модели KPI
    "HeadPremium",
    "SpecKPI",
    "SpecPremium",
    # Модели Gifter
    "Event",
    "User",
    "UserEvent",
    # Модели Questioner
    "Question",
    "MessagesPair",
    "Settings",
    # Репозитории запросов
    "KPIRequestsRepo",
    "MainRequestsRepo",
    "QuestionsRequestsRepo",
    # Репозитории STP
    "AchievementsRepo",
    "BroadcastRepo",
    "EmployeeRepo",
    "FilesRepo",
    "GroupRepo",
    "GroupMemberRepo",
    "ProductsRepo",
    "PurchaseRepo",
    "TransactionRepo",
    "EventLog",
    "EventLogRepo",
    "Exchange",
    "ExchangeSubscription",
    "ExchangeRepo",
    # Репозитории KPI
    "HeadPremiumRepo",
    "SpecKPIRepo",
    "SpecPremiumRepo",
    "MessagesPair",
    "Question",
    "Settings",
]
