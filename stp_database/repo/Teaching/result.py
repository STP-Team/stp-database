"""Репозиторий функций для взаимодействия с таблицей результатов опроса."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Teaching.result import Result
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class ResultsRepo(BaseRepo):
    """Класс репозитория опроса."""

    async def add_result(
        self,
        user_id: int,
        first_q: str,
        second_q: str,
        third_q: str,
        fourth_q: str,
        fifth_q: str,
        sixth_q: str,
    ) -> Result | None:
        """Добавление нового результата.

        Args:

        Returns:
            Созданный объект Result или None в случае ошибки
        """
        new_result = Result(
            user_id=user_id,
            first_q=first_q,
            second_q=second_q,
            third_q=third_q,
            fourth_q=fourth_q,
            fifth_q=fifth_q,
            sixth_q=sixth_q,
        )

        try:
            self.session.add(new_result)
            await self.session.commit()
            await self.session.refresh(new_result)
            logger.info(f"[БД] Создан новый результат: {user_id}")
            return new_result
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления результата {user_id}: {e}")
            await self.session.rollback()
            return None

    async def get_result(
        self,
        user_id: int,
    ) -> Result | None:
        """Получение результата по user_id.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Объект Result или None
        """
        select_stmt = select(Result).where(Result.user_id == user_id)

        result = await self.session.execute(select_stmt)
        return result.scalar_one_or_none()

    async def update_result(
        self,
        result_id: int,
        **kwargs: Any,
    ) -> Result | None:
        """Обновление результата.

        Args:
            result_id: Идентификатор результата

        Returns:
            Обновленный объект Result или None
        """
        select_stmt = select(Result).where(Result.id == result_id)

        result = await self.session.execute(select_stmt)
        result_obj: Result | None = result.scalar_one_or_none()

        # Если результат существует - обновляем его
        if result_obj:
            for key, value in kwargs.items():
                setattr(result_obj, key, value)
            await self.session.commit()
            await self.session.refresh(result_obj)
            logger.info(f"[БД] Результат с ID {result_id} успешно обновлен")

        return result_obj

    async def delete_result(
        self,
        result_id: int,
    ) -> bool:
        """Удаление результата.

        Args:
            result_id: Идентификатор результата

        Returns:
            True если успешно, иначе False
        """
        try:
            select_stmt = select(Result).where(Result.id == result_id)
            result = await self.session.execute(select_stmt)
            result_obj = result.scalar_one_or_none()

            if result_obj is None:
                logger.warning(f"[БД] Результат с ID {result_id} не найден")
                return False

            await self.session.delete(result_obj)
            await self.session.commit()
            logger.info(f"[БД] Результат с ID {result_id} успешно удален")
            return True

        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка удаления результата с ID {result_id}: {e}")
            await self.session.rollback()
            return False
