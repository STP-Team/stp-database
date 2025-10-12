"""Репозиторий для работы с моделями БД Questions."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stp_database.repo.Questions.pairs import MessagesPairsRepo
from stp_database.repo.Questions.questions import QuestionsRepo
from stp_database.repo.Questions.settings import SettingsRepo


@dataclass
class QuestionsRequestsRepo:
    """Репозиторий для обработки операций с БД. Этот класс содержит все репозитории для моделей базы данных Questions.

    Ты можешь добавить дополнительные репозитории в качестве свойств к этому классу, чтобы они были легко доступны.
    """

    session: AsyncSession

    @property
    def questions(self) -> QuestionsRepo:
        """Инициализация репозитория QuestionsRepo с сессией для работы с вопросами."""
        return QuestionsRepo(self.session)

    @property
    def messages_pairs(self) -> MessagesPairsRepo:
        """Инициализация репозитория MessagesPairsRepo с сессией для работы с парами сообщений."""
        return MessagesPairsRepo(self.session)

    @property
    def settings(self) -> SettingsRepo:
        """Инициализация репозитория MessagesPairsRepo с сессией для работы с настройками Вопросника в группах."""
        return SettingsRepo(self.session)
