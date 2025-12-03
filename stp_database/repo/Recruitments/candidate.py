"""Репозиторий функций для работы с кандидатами."""

import logging
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Recruitments.candidates import Candidate
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class CandidateRepo(BaseRepo):
    """Репозиторий для работы с кандидатами."""

    async def add_candidate(
        self,
        user_id: int,
        position: str,
    ) -> Candidate | None:
        """Добавление нового кандидата.

        Args:
            user_id: Идентификатор Telegram кандидата
            position: Название позиции, на которую подается кандидат

        Returns:
            Созданный объект Candidate или None в случае ошибки
        """
        new_candidate = Candidate(
            user_id=user_id,
            position=position,
        )

        try:
            self.session.add(new_candidate)
            await self.session.commit()
            await self.session.refresh(new_candidate)
            logger.info(f"[БД] Создан новый кандидат: {user_id}")
            return new_candidate
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления пользователя {user_id}: {e}")
            await self.session.rollback()
            return None

    async def update_candidate(
        self,
        user_id: int = None,
        **kwargs: Any,
    ) -> Candidate | None:
        """Обновление кандидата.

        Args:
            user_id: Идентификатор Telegram кандидата
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект Candidate или None
        """
        select_stmt = select(Candidate).where(Candidate.user_id == user_id)

        result = await self.session.execute(select_stmt)
        candidate: Candidate | None = result.scalar_one_or_none()

        # Если кандидат существует - обновляем его
        if candidate:
            for key, value in kwargs.items():
                setattr(candidate, key, value)
            await self.session.commit()

        return candidate

    async def get_candidate(
        self, user_id: int = None, topic_id: int = None
    ) -> Candidate | None:
        """Получение информации о кандидате по его user_id.

        Args:
            user_id: Идентификатор Telegram кандидата
            topic_id: Идентификатор топика, которому принадлежит кандидат

        Returns:
            Объект Candidate
        """
        if user_id:
            select_stmt = select(Candidate).where(Candidate.user_id == user_id)
        elif topic_id:
            select_stmt = select(Candidate).where(Candidate.topic_id == topic_id)
        else:
            return None

        result = await self.session.execute(select_stmt)

        return result.scalar_one_or_none()

    async def get_candidates_by_status(self, status: str) -> Sequence[Candidate]:
        """Получение всех кандидатов с определенным статусом.

        Args:
            status: Статус кандидатов для поиска

        Returns:
            Список объектов Candidate с указанным статусом
        """
        select_stmt = select(Candidate).where(Candidate.status == status)
        result = await self.session.execute(select_stmt)
        return result.scalars().all()
