"""Репозиторий функций для взаимодействия с таблицей рассылок."""

import logging
from typing import Any, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.broadcast import Broadcast
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class BroadcastRepo(BaseRepo):
    """Репозиторий для работы с рассылками."""

    async def get_broadcasts(
        self,
        broadcast_id: Optional[int] = None,
        user_id: Optional[int] = None,
        broadcast_type: Optional[str] = None,
        target: Optional[str] = None,
    ) -> Optional[Broadcast] | Sequence[Broadcast]:
        """Поиск рассылки или списка рассылок.

        Args:
            broadcast_id: Уникальный идентификатор рассылки (если указан, возвращает одну рассылку)
            user_id: Идентификатор владельца рассылки
            broadcast_type: Тип рассылки (division/group)
            target: Цель рассылки

        Returns:
            Объект Broadcast или None (если указан broadcast_id)
            Последовательность Broadcast (если broadcast_id не указан)
        """
        filters = []

        if broadcast_id is not None:
            filters.append(Broadcast.id == broadcast_id)
        if user_id:
            filters.append(Broadcast.user_id == user_id)
        if broadcast_type:
            filters.append(Broadcast.type == broadcast_type)
        if target:
            filters.append(Broadcast.target == target)

        query = select(Broadcast)
        if filters:
            query = query.where(*filters)

        # Если запрашивается одна рассылка по ID
        if broadcast_id is not None:
            try:
                result = await self.session.execute(query)
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка получения рассылки: {e}")
                return None
        else:
            # Запрос списка рассылок
            query = query.order_by(Broadcast.created_at.desc())
            try:
                result = await self.session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка получения списка рассылок: {e}")
                return []

    async def update_broadcast(
        self,
        broadcast_id: int,
        **kwargs: Any,
    ) -> Optional[Broadcast]:
        """Обновление рассылки.

        Args:
            broadcast_id: Идентификатор рассылки для обновления
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект Broadcast или None
        """
        select_stmt = select(Broadcast).where(Broadcast.id == broadcast_id)

        result = await self.session.execute(select_stmt)
        broadcast: Broadcast | None = result.scalar_one_or_none()

        # Если рассылка существует - обновляем её
        if broadcast:
            for key, value in kwargs.items():
                setattr(broadcast, key, value)
            try:
                await self.session.commit()
                logger.info(f"[БД] Рассылка {broadcast_id} обновлена")
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка обновления рассылки {broadcast_id}: {e}")
                await self.session.rollback()
                return None

        return broadcast

    async def delete_broadcast(self, broadcast_id: int) -> bool:
        """Удаление рассылки.

        Args:
            broadcast_id: ID рассылки для удаления

        Returns:
            True если рассылка была удалена, False в случае ошибки
        """
        try:
            # Находим рассылку по ID
            query = select(Broadcast).where(Broadcast.id == broadcast_id)
            result = await self.session.execute(query)
            broadcast = result.scalar_one_or_none()

            if broadcast:
                await self.session.delete(broadcast)
                await self.session.commit()
                logger.info(f"[БД] Рассылка {broadcast_id} удалена из базы")
                return True
            else:
                logger.warning(f"[БД] Рассылка с ID {broadcast_id} не найдена")
                return False

        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка удаления рассылки {broadcast_id}: {e}")
            await self.session.rollback()
            return False

    async def create_broadcast(
        self,
        user_id: int,
        broadcast_type: str,
        target: str,
        text: str,
        recipients: Optional[List[int]] = None,
    ) -> Optional[Broadcast]:
        """Создание рассылки.

        Args:
            user_id: Идентификатор Telegram владельца рассылки
            broadcast_type: Тип рассылки (division/group)
            target: Цель рассылки
            text: Текст рассылки
            recipients: Список получателей

        Returns:
            Созданный объект Broadcast или None в случае ошибки
        """
        try:
            broadcast = Broadcast(
                user_id=user_id,
                type=broadcast_type,
                target=target,
                text=text,
                recipients=recipients,
            )

            self.session.add(broadcast)
            await self.session.commit()
            logger.info(f"[БД] Создана новая рассылка ID: {broadcast.id}")
            return broadcast

        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка создания рассылки: {e}")
            await self.session.rollback()
            return None
