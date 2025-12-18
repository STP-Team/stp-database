"""Репозиторий функций для работы с премией руководителей."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Stats.head_premium import HeadPremium
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class HeadPremiumRepo(BaseRepo):
    """Репозиторий с функциями для работы с премией руководителей."""

    async def get_premium(
        self, fullnames: str | list[str], extraction_period: datetime
    ) -> HeadPremium | None | Sequence[HeadPremium]:
        """Поиск показателей премии руководителей в БД по ФИО.

        Args:
            fullnames: ФИО руководителя или список ФИО руководителей в БД
            extraction_period: Дата выгрузки премиума

        Returns:
            HeadPremium или ничего (если передана строка)
            Список объектов HeadPremium (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        is_single = isinstance(fullnames, str)

        if is_single:
            query = select(HeadPremium).where(
                HeadPremium.fullname == fullnames,
                HeadPremium.extraction_period == extraction_period,
            )
        else:
            if not fullnames:
                return []
            query = select(HeadPremium).where(
                HeadPremium.fullname.in_(fullnames),
                HeadPremium.extraction_period == extraction_period,
            )

        try:
            result = await self.session.execute(query)
            if is_single:
                return result.scalar_one_or_none()
            else:
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения показателей премиума руководителя(-ей): {e}"
            )
            return None if is_single else []

    async def update_premium(
        self,
        extraction_period: datetime,
        fullname: str,
        **kwargs: Any,
    ) -> HeadPremium | None:
        """Обновление премиума.

        Args:
            **kwargs: Параметры для обновления
            extraction_period:

        Returns:
            Обновленный объект HeadPremium или None
        """
        select_stmt = select(HeadPremium).where(
            HeadPremium.fullname == fullname,
            HeadPremium.extraction_period == extraction_period,
        )

        result = await self.session.execute(select_stmt)
        premium: HeadPremium | None = result.scalar_one_or_none()

        # Если строка существует - обновляем ее
        if premium:
            for key, value in kwargs.items():
                setattr(premium, key, value)
            await self.session.commit()

        return premium
