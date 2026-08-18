"""Модели базы Notifications."""

from stp_database.models.Notifications.notification import (
    Notification,
    NotificationRecipient,
)

__all__ = [
    "Notification",
    "NotificationRecipient",
]