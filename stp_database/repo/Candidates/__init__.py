"""Репозитории базы Candidates."""

from .candidate import CandidateRepo
from .form import FormRepo
from .message import MessageRepo
from .requests import CandidatesRequestsRepo

__all__ = [
    "CandidateRepo",
    "FormRepo",
    "MessageRepo",
    "CandidatesRequestsRepo",
]