"""Репозиторий функций для взаимодействия с таблицей достижений."""

from typing import Optional, Sequence

from sqlalchemy import select

from stp_database.models.STP.achievement import Achievement
from stp_database.repo.base import BaseRepo


class AchievementsRepo(BaseRepo):
    """Класс репозитория достижений."""

    async def get_achievements(self, division: str = None) -> Sequence[Achievement]:
        """Получает полный список достижений.

        Args:
            division: Фильтр по направлению (НЦК, НТП и т.д.)

        Returns:
            Последовательность Achievement. С фильтрацией по направлению, если указан division
        """
        if division:
            select_stmt = select(Achievement).where(Achievement.division == division)
        else:
            select_stmt = select(Achievement)

        result = await self.session.execute(select_stmt)
        achievements = result.scalars().all()

        return list(achievements)

    async def get_achievement(self, achievement_id: int) -> Optional[Achievement]:
        """Получает информацию о достижении по идентификатору.

        Args:
            achievement_id: Уникальный идентификатор достижения в таблице achievements

        Returns:
            Achievement, если достижение найдено, иначе None
        """
        select_stmt = select(Achievement).where(Achievement.id == achievement_id)
        result = await self.session.execute(select_stmt)

        return result.scalar_one()
