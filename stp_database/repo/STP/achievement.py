"""Репозиторий функций для взаимодействия с таблицей достижений."""

from typing import Sequence

from sqlalchemy import select

from stp_database.models.STP.achievement import Achievement
from stp_database.repo.base import BaseRepo


class AchievementsRepo(BaseRepo):
    """Класс репозитория достижений."""

    async def get_achievements(
        self,
        achievement_id: int | None = None,
        division: str | None = None,
    ) -> Achievement | None | Sequence[Achievement]:
        """Получает достижение(я) по идентификатору или список достижений.

        Args:
            achievement_id: Уникальный идентификатор достижения (если указан, возвращает одно достижение)
            division: Фильтр по направлению (НЦК, НТП и т.д.) - используется только если achievement_id не указан

        Returns:
            Achievement или None (если указан achievement_id)
            Последовательность Achievement (если achievement_id не указан)
        """
        if achievement_id is not None:
            # Запрос одного достижения по ID
            select_stmt = select(Achievement).where(Achievement.id == achievement_id)
            result = await self.session.execute(select_stmt)
            return result.scalar_one_or_none()
        else:
            # Запрос списка достижений с опциональной фильтрацией по division
            if division:
                select_stmt = select(Achievement).where(
                    Achievement.division == division
                )
            else:
                select_stmt = select(Achievement)

            result = await self.session.execute(select_stmt)
            achievements = result.scalars().all()

            return list(achievements)
