"""Универсальные модели для наследования."""

from datetime import datetime

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(primary_key=True)]


class TableNameMixin:
    """Миксин для названия таблиц."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Добавление 's' к концу названия класса."""
        return self.__name__.lower() + "s"


class TimestampMixin:
    """Миксин для даты создания."""

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
