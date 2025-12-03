"""Репозиторий для работы с моделями БД Questions."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.repo.Recruitments.candidate import CandidateRepo


@dataclass
class RecruitmentsRequestsRepo:
    """Репозиторий для обработки операций с БД. Этот класс содержит все репозитории для моделей базы данных Recruitments.

    Ты можешь добавить дополнительные репозитории в качестве свойств к этому классу, чтобы они были легко доступны.
    """

    session: AsyncSession

    @property
    def candidates(self) -> CandidateRepo:
        """Инициализация репозитория CandidateRepo с сессией для работы с кандидатами."""
        return CandidateRepo(self.session)
