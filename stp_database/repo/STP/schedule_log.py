"""Репозиторий для работы с логами расписания."""

import logging
from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.schedule import Schedule
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class ScheduleLogRepo(BaseRepo):
    """Репозиторий для работы с логами расписания."""

    async def get_files_history(
        self,
        file_id: Optional[str] = None,
        uploaded_by_user_id: Optional[int] = None,
        uploaded_from: Optional[datetime] = None,
        uploaded_to: Optional[datetime] = None,
    ) -> Sequence[Schedule]:
        """Получение записей лога расписания по фильтрам.

        Args:
            file_id: Идентификатор Telegram файла
            uploaded_by_user_id: ID пользователя, загрузившего файл
            uploaded_from: Начало периода времени загрузки
            uploaded_to: Конец периода времени загрузки

        Returns:
            Список объектов ScheduleLog
        """
        filters = []

        if file_id:
            filters.append(Schedule.file_id == file_id)
        if uploaded_by_user_id:
            filters.append(Schedule.uploaded_by_user_id == uploaded_by_user_id)
        if uploaded_from:
            filters.append(Schedule.uploaded_at >= uploaded_from)
        if uploaded_to:
            filters.append(Schedule.uploaded_at <= uploaded_to)

        query = select(Schedule).order_by(Schedule.uploaded_at.desc())
        if filters:
            query = query.where(and_(*filters))

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения записей ScheduleLog: {e}")
            return []

    async def add_file_history(self, **kwargs: Any) -> Optional[Schedule]:
        """Добавление новой записи в логи расписания.

        Args:
            kwargs: Параметры для создания записи ScheduleLog

        Returns:
            Новый объект ScheduleLog или None при ошибке
        """
        file_entry = Schedule(**kwargs)
        self.session.add(file_entry)
        try:
            await self.session.commit()
            await self.session.refresh(file_entry)
            return file_entry
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления записи ScheduleLog: {e}")
            await self.session.rollback()
            return None
