"""Репозиторий для работы с моделями БД STP."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.repo.Teaching.result import ResultsRepo


@dataclass
class TeachingsRepo:
    """Репозиторий для обработки операций с БД. Этот класс содержит все репозитории для моделей базы данных Teaching.

    Ты можешь добавить дополнительные репозитории в качестве свойств к этому классу, чтобы они были легко доступны.
    """

    session: AsyncSession

    @property
    def results(self) -> ResultsRepo:
        """Инициализация репозитория ResultsRepo с сессией для работы с записями результатов."""
        return ResultsRepo(self.session)
