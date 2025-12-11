"""Репозиторий функций для работы с премией специалистов."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.KPI.spec_premium import SpecPremium
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class SpecPremiumRepo(BaseRepo):
    """Репозиторий с функциями для работы с премией специалистов."""

    async def get_premium(
        self,
        fullnames: str | list[str],
    ) -> SpecPremium | None | Sequence[SpecPremium]:
        """Поиск показателей премии специалистов в БД по ФИО.

        Args:
            fullnames: ФИО специалиста или список ФИО специалистов в БД

        Returns:
            SpecPremium или ничего (если передана строка)
            Список объектов SpecPremium (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        is_single = isinstance(fullnames, str)

        if is_single:
            query = select(SpecPremium).where(SpecPremium.fullname == fullnames)
        else:
            if not fullnames:
                return []
            query = select(SpecPremium).where(SpecPremium.fullname.in_(fullnames))

        try:
            result = await self.session.execute(query)
            if is_single:
                return result.scalar_one_or_none()
            else:
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения показателей премиума специалиста(-ов): {e}"
            )
            return None if is_single else []

    async def update_premium(
        self,
        extraction_period: datetime,
        fullname: str,
        **kwargs: Any,
    ) -> SpecPremium | None:
        """Обновление премиума.

        Args:
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект Employee или None
        """
        select_stmt = select(SpecPremium).where(
            SpecPremium.fullname == fullname,
            SpecPremium.extraction_period == extraction_period,
        )

        result = await self.session.execute(select_stmt)
        user: SpecPremium | None = result.scalar_one_or_none()

        # Если строка существует - обновляем ее
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.session.commit()

        return user
