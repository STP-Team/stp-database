"""Репозиторий внутренних уведомлений STPsher."""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Notifications import (
    Notification,
    NotificationRecipient,
)
from stp_database.repo.base import BaseRepo


logger = logging.getLogger(__name__)


class NotificationRepo(BaseRepo):
    """Работа с уведомлениями STPsher."""

    async def create_notification(
        self,
        *,
        title: str,
        text: str,
        notification_type: str,
        recipient_ids: list[int],
        created_by: int | None = None,
        action: str | None = None,
        action_data: dict[str, Any] | None = None,
    ) -> Notification | None:
        """
        Создать уведомление.

        recipient_ids содержит employees.id
        из основной БД STP.
        """

        unique_recipient_ids = sorted(
            {
                int(employee_id)
                for employee_id
                in recipient_ids
            }
        )

        if not unique_recipient_ids:
            return None

        try:
            notification = Notification(
                title=title,
                text=text,
                type=notification_type,
                action=action,
                action_data=action_data,
                created_by=created_by,
            )

            self.session.add(
                notification
            )

            await self.session.flush()

            recipients = [
                NotificationRecipient(
                    notification_id=int(
                        notification.id
                    ),
                    employee_id=employee_id,
                )
                for employee_id
                in unique_recipient_ids
            ]

            self.session.add_all(
                recipients
            )

            await self.session.commit()

            await self.session.refresh(
                notification
            )

            logger.info(
                "[Notifications] Создано уведомление %s "
                "для %s получателей",
                notification.id,
                len(unique_recipient_ids),
            )

            return notification

        except SQLAlchemyError as exc:
            logger.error(
                "[Notifications] Ошибка создания "
                "уведомления: %s",
                exc,
            )

            await self.session.rollback()

            return None

    async def get_user_notifications(
        self,
        *,
        employee_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[
        list[
            tuple[
                Notification,
                datetime | None,
            ]
        ],
        int,
        int,
    ]:
        """
        Получить уведомления сотрудника.

        Возвращает:
        rows,
        total,
        unread_count.
        """

        try:
            statement = (
                select(
                    Notification,
                    NotificationRecipient.read_at,
                )
                .join(
                    NotificationRecipient,
                    NotificationRecipient.notification_id
                    == Notification.id,
                )
                .where(
                    NotificationRecipient.employee_id
                    == int(employee_id)
                )
                .order_by(
                    Notification.created_at.desc(),
                    Notification.id.desc(),
                )
                .offset(
                    skip
                )
                .limit(
                    limit
                )
            )

            result = await self.session.execute(
                statement
            )

            rows = [
                (
                    row[0],
                    row[1],
                )
                for row
                in result.all()
            ]

            total_statement = (
                select(
                    func.count()
                )
                .select_from(
                    NotificationRecipient
                )
                .where(
                    NotificationRecipient.employee_id
                    == int(employee_id)
                )
            )

            total_result = (
                await self.session.execute(
                    total_statement
                )
            )

            total = int(
                total_result.scalar_one()
                or 0
            )

            unread_statement = (
                select(
                    func.count()
                )
                .select_from(
                    NotificationRecipient
                )
                .where(
                    NotificationRecipient.employee_id
                    == int(employee_id),
                    NotificationRecipient.read_at.is_(
                        None
                    ),
                )
            )

            unread_result = (
                await self.session.execute(
                    unread_statement
                )
            )

            unread_count = int(
                unread_result.scalar_one()
                or 0
            )

            return (
                rows,
                total,
                unread_count,
            )

        except SQLAlchemyError as exc:
            logger.error(
                "[Notifications] Ошибка получения "
                "уведомлений employee_id=%s: %s",
                employee_id,
                exc,
            )

            return (
                [],
                0,
                0,
            )

    async def get_unread_count(
        self,
        *,
        employee_id: int,
    ) -> int:
        """Получить количество непрочитанных."""

        try:
            statement = (
                select(
                    func.count()
                )
                .select_from(
                    NotificationRecipient
                )
                .where(
                    NotificationRecipient.employee_id
                    == int(employee_id),
                    NotificationRecipient.read_at.is_(
                        None
                    ),
                )
            )

            result = await self.session.execute(
                statement
            )

            return int(
                result.scalar_one()
                or 0
            )

        except SQLAlchemyError as exc:
            logger.error(
                "[Notifications] Ошибка получения "
                "unread_count: %s",
                exc,
            )

            return 0

    async def mark_read(
        self,
        *,
        notification_id: int,
        employee_id: int,
    ) -> bool:
        """
        Отметить уведомление прочитанным.

        Повторный вызов безопасен:
        исходный read_at сохраняется.
        """

        try:
            statement = (
                update(
                    NotificationRecipient
                )
                .where(
                    NotificationRecipient.notification_id
                    == int(notification_id),
                    NotificationRecipient.employee_id
                    == int(employee_id),
                )
                .values(
                    read_at=func.coalesce(
                        NotificationRecipient.read_at,
                        func.current_timestamp(),
                    )
                )
            )

            result = await self.session.execute(
                statement
            )

            await self.session.commit()

            return bool(
                result.rowcount
            )

        except SQLAlchemyError as exc:
            logger.error(
                "[Notifications] Ошибка отметки "
                "уведомления %s прочитанным: %s",
                notification_id,
                exc,
            )

            await self.session.rollback()

            return False

    async def mark_all_read(
        self,
        *,
        employee_id: int,
    ) -> int:
        """Отметить все уведомления прочитанными."""

        try:
            statement = (
                update(
                    NotificationRecipient
                )
                .where(
                    NotificationRecipient.employee_id
                    == int(employee_id),
                    NotificationRecipient.read_at.is_(
                        None
                    ),
                )
                .values(
                    read_at=func.current_timestamp()
                )
            )

            result = await self.session.execute(
                statement
            )

            await self.session.commit()

            return int(
                result.rowcount
                or 0
            )

        except SQLAlchemyError as exc:
            logger.error(
                "[Notifications] Ошибка MarkAllRead: %s",
                exc,
            )

            await self.session.rollback()

            return 0