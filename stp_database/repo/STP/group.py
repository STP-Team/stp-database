"""Репозиторий функций для взаимодействия с группами."""

import logging
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.group import Group
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class GroupRepo(BaseRepo):
    """Репозиторий для работы с группами."""

    async def get_groups(
        self,
        group_id: int | None = None,
        invited_by: int | None = None,
    ) -> Group | None | Sequence[Group | None]:
        """Получить группу или список групп.

        Args:
            group_id: Идентификатор группы Telegram (если указан, возвращает одну группу)
            invited_by: Идентификатор пользователя, который пригласил бота (фильтр для списка групп)

        Returns:
            Объект Group или None (если указан group_id)
            Последовательность Group (если group_id не указан)
        """
        if group_id is not None:
            # Запрос одной группы по ID
            try:
                result = await self.session.execute(
                    select(Group).where(Group.group_id == group_id)
                )
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка получения группы {group_id}: {e}")
                return None
        else:
            # Запрос списка групп
            query = select(Group)

            if invited_by is not None:
                query = query.where(Group.invited_by == invited_by)

            try:
                result = await self.session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                if invited_by is not None:
                    logger.error(
                        f"[БД] Ошибка получения групп для пользователя {invited_by}: {e}"
                    )
                else:
                    logger.error(f"[БД] Ошибка получения списка всех групп: {e}")
                return []

    async def add_group(
        self, group_id: int, group_type: str, invited_by: int
    ) -> Group | None:
        """Добавить группу.

        Args:
            group_id: Идентификатор группы Telegram
            group_type: Тип группы (group или channel)
            invited_by: Идентификатор Telegram пользователя, пригласившего бота

        Returns:
            Объект Group или None при ошибке
        """
        try:
            group = Group(
                group_id=group_id, group_type=group_type, invited_by=invited_by
            )
            self.session.add(group)
            await self.session.commit()
            return group
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления группы {group_id}: {e}")
            await self.session.rollback()
            return None

    async def update_group(
        self,
        group_id: int = None,
        **kwargs: Any,
    ) -> Group | None:
        """Обновление группы.

        Args:
            group_id: Идентификатор группы для обновления
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект Group или None
        """
        try:
            select_stmt = select(Group).where(Group.group_id == group_id)

            result = await self.session.execute(select_stmt)
            group: Group | None = result.scalar_one_or_none()

            # Если группа существует - обновляем ее
            if group is not None:
                for key, value in kwargs.items():
                    setattr(group, key, value)
                await self.session.commit()
                logger.info(f"[БД] Группа {group_id} обновлена: {kwargs}")
            else:
                logger.warning(f"[БД] Группа {group_id} не найдена для обновления")

            return group
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка обновления группы {group_id}: {e}")
            await self.session.rollback()
            return None

    async def delete_group(self, group_id: int) -> bool:
        """Удаление группы.

        Args:
            group_id: Идентификатор группы Telegram

        Returns:
            True если группа удалена, False при ошибке
        """
        try:
            result = await self.session.execute(
                select(Group).where(Group.group_id == group_id)
            )
            group = result.scalar_one_or_none()

            if group:
                await self.session.delete(group)
                await self.session.commit()
                logger.info(f"[БД] Группа {group_id} удалена")
                return True
            else:
                logger.warning(f"[БД] Группа {group_id} не найдена для удаления")
                return False
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка удаления группы {group_id}: {e}")
            await self.session.rollback()
            return False
