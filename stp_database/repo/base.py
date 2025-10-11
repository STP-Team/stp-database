from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    """Класс, представляющий базовый репозиторий для обработки операций с базой данных."""

    def __init__(self, session):
        self.session: AsyncSession = session
