"""Инициализация моделей Гифтера."""

from .events import Event
from .user import User
from .users_events import UserEvent

__all__ = ["User", "Event", "UserEvent"]
