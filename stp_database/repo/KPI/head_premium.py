"""Репозиторий функций для работы с премией руководителей."""

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.KPI.head_premium import HeadPremium
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class HeadPremiumRepo(BaseRepo):
    """Репозиторий с функциями для работы с премией руководителей."""

    async def get_premium(
        self,
        fullnames: str | list[str],
    ) -> HeadPremium | None | Sequence[HeadPremium]:
        """Поиск показателей премии руководителей в БД по ФИО.

        Args:
            fullnames: ФИО руководителя или список ФИО руководителей в БД

        Returns:
            HeadPremium или ничего (если передана строка)
            Список объектов HeadPremium (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        is_single = isinstance(fullnames, str)

        if is_single:
            query = select(HeadPremium).where(HeadPremium.fullname == fullnames)
        else:
            if not fullnames:
                return []
            query = select(HeadPremium).where(HeadPremium.fullname.in_(fullnames))

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
