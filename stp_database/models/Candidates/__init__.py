"""Инициализация моделей базы Candidates."""

from .candidate import Candidate
from .form import Form
from .message import Message

__all__ = [
    "Candidate",
    "Form",
    "Message",
]