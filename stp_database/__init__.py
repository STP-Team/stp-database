"""Управление БД СТП."""

__version__ = "3.0"

from stp_database.config import DbConfig
from stp_database.models.base import Base
from stp_database.repo.base import BaseRepo
from stp_database.setup import create_engine, create_session_pool

__all__ = [
    "__version__",
    "DbConfig",
    "create_engine",
    "create_session_pool",
    "Base",
    "BaseRepo",
]
