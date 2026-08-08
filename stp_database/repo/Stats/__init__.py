"""Репозитории для работы с таблицами системы Stats."""

from .requests import StatsRequestsRepo
from .questioner import QuestionerChatsRepo

__all__ = [
    "StatsRequestsRepo",
    "QuestionerChatsRepo",
]
