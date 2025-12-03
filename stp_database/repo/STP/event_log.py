"""Репозиторий для работы с логами ивентов."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP import EventLog
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class EventLogRepo(BaseRepo):
    """Репозиторий для работы с логами событий."""

    async def create_event(
        self,
        user_id: int,
        event_type: str,
        event_category: str,
        session_id: str | None = None,
        dialog_state: str | None = None,
        window_name: str | None = None,
        action: str | None = None,
        metadata: dict | None = None,
    ) -> EventLog | None:
        """Создание записи события в базе данных.

        Args:
            user_id: Идентификатор сотрудника
            event_type: Тип события (например, 'click', 'login', 'logout')
            event_category: Категория события (например, 'UI', 'System', 'Network')
            session_id: Идентификатор сессии (опционально)
            dialog_state: Состояние диалога на момент события (опционально)
            window_name: Имя окна или экрана, где произошло событие (опционально)
            action: Действие, совершённое пользователем (опционально)
            metadata: Дополнительные данные события в формате JSON (опционально)

        Returns:
            Созданный объект EventLog или None в случае ошибки
        """
        new_event = EventLog(
            user_id=user_id,
            event_type=event_type,
            event_category=event_category,
            session_id=session_id,
            dialog_state=dialog_state,
            window_name=window_name,
            action=action,
            event_metadata=metadata,
        )

        try:
            self.session.add(new_event)
            await self.session.commit()
            await self.session.refresh(new_event)
            logger.debug(
                f"Event created: type={event_type}, category={event_category}, user_id={user_id}"
            )
            return new_event
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating event: {e}")
            return None
