"""Репозиторий функций для работы с настройками групп Вопросника."""

import json
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import func, select

from stp_database import BaseRepo, Settings


class SettingsRepo(BaseRepo):
    """Репозиторий с функциями для работы с настройками групп."""

    async def add_settings(
        self,
        group_id: int,
        values: Optional[Dict[str, Any]] = None,
    ) -> Settings:
        """Добавление группы в настройки.

        Args:
            group_id: ID группы Telegram
            values: Словарь с настройками (по умолчанию пустой)

        Returns:
            Созданный объект Settings
        """
        if values is None:
            values = {}

        settings = Settings(
            group_id=group_id,
            values=json.dumps(values, ensure_ascii=False),
        )

        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)

        return settings

    async def get_settings_by_group_id(self, group_id: int) -> Optional[Settings]:
        """Получение настроек группы по идентификатору группы.

        Args:
            group_id: Идентификатор группы Telegram

        Returns:
            Объект Settings если наши, иначе None
        """
        stmt = select(Settings).where(Settings.group_id == group_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_settings_by_id(self, settings_id: int) -> Optional[Settings]:
        """Получение настроек группы по идентификатору записи.

        Args:
            settings_id: Идентификатор записи настроек

        Returns:
            Объект Settings или None, если не найден
        """
        return await self.session.get(Settings, settings_id)

    async def get_all_settings(self) -> Sequence[Settings]:
        """Получение настроек всех групп.

        Returns:
             Последовательность настроек всех групп
        """
        stmt = select(Settings).order_by(Settings.last_update.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_settings(
        self, group_id: int, values: Dict[str, Any]
    ) -> Optional[Settings]:
        """Обновление настроек группы.

        Args:
            group_id: ID группы Telegram
            values: Новые значения настроек

        Returns:
            Обновленный объект Settings или None, если не найден
        """
        settings = await self.get_settings_by_group_id(group_id)
        if settings is None:
            return None

        settings.set_values(values)
        settings.last_update = func.now()

        await self.session.commit()
        await self.session.refresh(settings)

        return settings

    async def update_setting(
        self, group_id: int, key: str, value: Any
    ) -> Optional[Settings]:
        """Обновление настройки.

        Args:
            group_id: ID группы Telegram
            key: Ключ настройки
            value: Новое значение

        Returns:
            Обновленный объект Settings или None, если не найден
        """
        settings = await self.get_settings_by_group_id(group_id)
        if settings is None:
            return None

        settings.set_setting(key, value)
        settings.last_update = func.now()

        await self.session.commit()
        await self.session.refresh(settings)

        return settings

    async def get_or_create_settings(
        self, group_id: int, default_values: Optional[Dict[str, Any]] = None
    ) -> Settings:
        """Получение настроек или создание новых, если не существуют.

        Args:
            group_id: ID группы Telegram
            default_values: Значения по умолчанию для новых настроек

        Returns:
            Объект Settings
        """
        settings = await self.get_settings_by_group_id(group_id)
        if settings is None:
            if default_values is None:
                default_values = {
                    "ask_clever_link": True,
                    "activity_status": True,
                    "activity_warn_minutes": 5,
                    "activity_close_minutes": 10,
                }
            settings = await self.add_settings(group_id, default_values)

        return settings

    async def delete_settings(self, group_id: int) -> dict:
        """Удаление настроек группы.

        Args:
            group_id: Идентификатор группы Telegram

        Returns:
            Словарь с результатом удаления
        """
        try:
            settings = await self.get_settings_by_group_id(group_id)
            if settings is None:
                return {
                    "success": False,
                    "deleted_count": 0,
                    "errors": [f"Settings for group {group_id} not found"],
                }

            await self.session.delete(settings)
            await self.session.commit()

            return {
                "success": True,
                "deleted_count": 1,
                "errors": [],
            }

        except Exception as e:
            await self.session.rollback()
            error_msg = f"Database error: {str(e)}"
            return {
                "success": False,
                "deleted_count": 0,
                "errors": [error_msg],
            }

    async def get_settings_with_value(self, key: str, value: Any) -> Sequence[Settings]:
        """Получение всех настроек, где конкретный ключ имеет определенное значение.

        Args:
            key: Ключ настройки
            value: Искомое значение

        Returns:
            Последовательность найденных записей
        """
        all_settings = await self.get_all_settings()
        filtered_settings = []

        for settings in all_settings:
            if settings.get_setting(key) == value:
                filtered_settings.append(settings)

        return filtered_settings

    async def bulk_update_setting(
        self, group_ids: Sequence[int], key: str, value: Any
    ) -> dict:
        """Массовое обновление настройки для нескольких групп.

        Args:
            group_ids: Список ID групп
            key: Ключ настройки
            value: Новое значение

        Returns:
            Словарь с результатом операции
        """
        updated_count = 0
        errors = []

        try:
            for group_id in group_ids:
                try:
                    result = await self.update_setting(group_id, key, value)
                    if result:
                        updated_count += 1
                    else:
                        errors.append(f"Settings for group {group_id} not found")
                except Exception as e:
                    errors.append(f"Error updating group {group_id}: {str(e)}")

            return {
                "success": updated_count > 0,
                "updated_count": updated_count,
                "total_count": len(group_ids),
                "errors": errors,
            }

        except Exception as e:
            await self.session.rollback()
            error_msg = f"Database error: {str(e)}"
            return {
                "success": False,
                "updated_count": updated_count,
                "total_count": len(group_ids),
                "errors": [error_msg],
            }
