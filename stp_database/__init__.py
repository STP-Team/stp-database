"""
STP Database Package

A shared database layer for STP bots providing models, repositories, and database setup utilities.
"""

__version__ = "0.1.1"

# Core database setup
from stp_database.config import DbConfig
from stp_database.setup import create_engine, create_session_pool

# Base classes
from stp_database.models.base import Base, TableNameMixin, TimestampMixin
from stp_database.repo.base import BaseRepo

# Common models (exported from models/__init__.py)
from stp_database.models import Employee, Product

# Repository aggregators
from stp_database.repo.STP.requests import MainRequestsRepo
from stp_database.repo.KPI.requests import KPIRequestsRepo

__all__ = [
    # Version
    "__version__",
    # Config & Setup
    "DbConfig",
    "create_engine",
    "create_session_pool",
    # Base classes
    "Base",
    "TableNameMixin",
    "TimestampMixin",
    "BaseRepo",
    # Models
    "Employee",
    "Product",
    # Repositories
    "MainRequestsRepo",
    "KPIRequestsRepo",
]
