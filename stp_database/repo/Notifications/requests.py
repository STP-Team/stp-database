"""Агрегатор репозиториев базы Notifications."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.repo.Notifications.notification import (
    NotificationRepo,
)


@dataclass
class NotificationsRequestsRepo:
    """
    Репозитории базы Notifications.
    """

    session: AsyncSession

    @property
    def notification(self) -> NotificationRepo:
        return NotificationRepo(
            self.session
        )