"""Репозитории базы Notifications."""

from stp_database.repo.Notifications.notification import (
    NotificationRepo,
)
from stp_database.repo.Notifications.requests import (
    NotificationsRequestsRepo,
)

__all__ = [
    "NotificationRepo",
    "NotificationsRequestsRepo",
]