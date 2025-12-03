"""Репозиторий для работы с файлами."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.file import File
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class FilesRepo(BaseRepo):
    """Репозиторий для работы с файлами."""

    async def get_files(
        self,
        file_id: str | None = None,
        file_name: str | None = None,
        file_size: int | None = None,
        uploaded_by_user_id: int | None = None,
        uploaded_from: datetime | None = None,
        uploaded_to: datetime | None = None,
    ) -> Sequence[File]:
        """Получение записей файлов по фильтрам.

        Args:
            file_id: Идентификатор Telegram файла
            file_name: Название файла
            file_size: Размер файла в байтах
            uploaded_by_user_id: ID пользователя, загрузившего файл
            uploaded_from: Начало периода времени загрузки
            uploaded_to: Конец периода времени загрузки

        Returns:
            Список объектов File
        """
        filters = []

        if file_id:
            filters.append(File.file_id == file_id)
        if file_name:
            filters.append(File.file_name == file_name)
        if file_size is not None:
            filters.append(File.file_size == file_size)
        if uploaded_by_user_id:
            filters.append(File.uploaded_by_user_id == uploaded_by_user_id)
        if uploaded_from:
            filters.append(File.uploaded_at >= uploaded_from)
        if uploaded_to:
            filters.append(File.uploaded_at <= uploaded_to)

        query = select(File).order_by(File.uploaded_at.desc())
        if filters:
            query = query.where(and_(*filters))

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения записей файлов: {e}")
            return []

    async def get_file_by_id(
        self, main_id: int = None, file_id: str = None
    ) -> File | None:
        """Получение файла по его Telegram file_id.

        Args:
            main_id: Уникальный идентификатор файла
            file_id: Идентификатор Telegram файла

        Returns:
            Объект File или None, если файл не найден
        """
        if main_id:
            query = select(File).where(File.id == main_id)
        elif file_id:
            query = select(File).where(File.file_id == file_id)

        try:
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения файла по ID: {e}")
            return None

    async def add_file(self, **kwargs: Any) -> File | None:
        """Добавление нового файла.

        Args:
            kwargs: Параметры для создания записи File

        Returns:
            Новый объект File или None при ошибке
        """
        file_entry = File(**kwargs)
        self.session.add(file_entry)
        try:
            await self.session.commit()
            await self.session.refresh(file_entry)
            return file_entry
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления записи файла: {e}")
            await self.session.rollback()
            return None
