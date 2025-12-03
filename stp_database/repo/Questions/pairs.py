"""Репозиторий функций для работы с парами сообщений."""

from typing import Sequence

from sqlalchemy import and_, select

from stp_database import DbConfig
from stp_database.models.Questions.messages_pair import MessagesPair
from stp_database.repo.base import BaseRepo


class MessagesPairsRepo(BaseRepo):
    """Репозиторий с функциями для работы с парами сообщений между пользователем и дежурным."""

    async def add_pair(
        self,
        user_chat_id: int,
        user_message_id: int,
        topic_chat_id: int,
        topic_message_id: int,
        topic_thread_id: int | None,
        question_token: str,
        direction: str,
    ) -> MessagesPair:
        """Добавляет пару сообщения из чата пользователя и топика группы.

        Args:
            user_chat_id: Идентификатор Telegram специалиста
            user_message_id: Идентификатор Telegram сообщения в чате специалиста
            topic_chat_id: Идентификатор Telegram группы
            topic_message_id: Идентификатор Telegram сообщения в топике группы
            topic_thread_id: Идентификатор Telegram топика группы (опционально)
            question_token: Токен связанного вопроса
            direction: 'user_to_topic' или 'topic_to_user'

        Returns:
            Объект созданного MessagesPair
        """
        connection = MessagesPair(
            user_chat_id=user_chat_id,
            user_message_id=user_message_id,
            topic_chat_id=topic_chat_id,
            topic_message_id=topic_message_id,
            topic_thread_id=topic_thread_id,
            question_token=question_token,
            direction=direction,
        )

        self.session.add(connection)
        await self.session.commit()
        await self.session.flush()
        await self.session.refresh(connection)
        return connection

    async def find_by_user_message(
        self, user_chat_id: int, user_message_id: int
    ) -> MessagesPair | None:
        """Находит пару по сообщению специалиста.

        Args:
            user_chat_id: Идентификатор Telegram чата специалиста
            user_message_id: Идентификатор Telegram сообщения специалиста

        Returns:
            Объект MessagesPair, если удалось найти пару.
        """
        stmt = select(MessagesPair).where(
            and_(
                MessagesPair.user_chat_id == user_chat_id,
                MessagesPair.user_message_id == user_message_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_topic_message(
        self, topic_chat_id: int, topic_message_id: int
    ) -> MessagesPair | None:
        """Находит пару по сообщению в топике группы.

        Args:
            topic_chat_id: Идентификатор Telegram группы
            topic_message_id: Идентификатор Telegram сообщения в топике группы

        Returns:
            Объект MessagesPair, если удалось найти пару.
        """
        stmt = select(MessagesPair).where(
            and_(
                MessagesPair.topic_chat_id == topic_chat_id,
                MessagesPair.topic_message_id == topic_message_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_pair_for_edit(
        self, chat_id: int, message_id: int
    ) -> MessagesPair | None:
        """Находит пару сообщения для редактирования.

        Args:
            chat_id: Идентификатор чата Telegram с отредактированным сообщением
            message_id: Идентификатор отредактированного сообщения Telegra,

        Returns:
            Объект MessagesPair если пара найдена, иначе None
        """
        # Пытаемся найти по сообщению от пользователя
        connection = await self.find_by_user_message(chat_id, message_id)
        if connection:
            return connection

        # Пытаемся найти по сообщению в топиках
        connection: MessagesPair = await self.find_by_topic_message(chat_id, message_id)
        return connection

    async def get_pairs_by_question(self, question_token: str) -> list[MessagesPair]:
        """Получает все пары сообщений для вопроса.

        Args:
            question_token: Токен вопроса

        Returns:
            Список объектов MessagesPair
        """
        stmt = select(MessagesPair).where(MessagesPair.question_token == question_token)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_old_pairs(self) -> Sequence[MessagesPair]:
        """Получает пары сообщений старше 1 дня.

        Функция предназначена для использования при удалении старых вопросов.

        Returns:
            Последовательность объектов MessagesPair для удаления
        """
        from datetime import datetime, timedelta

        # Считаем дату день назад
        today = datetime.now(tz=DbConfig.tz)
        two_days_ago = today - timedelta(days=1)

        stmt = select(MessagesPair).where(MessagesPair.created_at < two_days_ago)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_pairs(self, pairs: Sequence[MessagesPair] = None) -> dict:
        """Удаляет старые пары сообщений из базы данных.

        Args:
            pairs: Последовательность объектов MessagesPair. Если не указано, получает их автоматически

        Returns:
            Результат операции с ключами:
                - success (bool): True если операция выполнена успешно
                - deleted_count (int): Количество удаленных связей
                - total_count (int): Общее количество связей для удаления
                - errors (list): Список ошибок, если они возникли
        """
        deleted_count = 0
        total_count = 0
        errors = []

        try:
            total_count = len(pairs)

            if total_count == 0:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "total_count": 0,
                    "errors": [],
                }

            # Удаляем каждую связь
            for connection in pairs:
                try:
                    # Обновляем объект в текущей сессии
                    await self.session.refresh(connection)
                    await self.session.delete(connection)
                    deleted_count += 1
                except Exception as e:
                    errors.append(
                        f"Error deleting connection {connection.id}: {str(e)}"
                    )

            await self.session.commit()

            return {
                "success": deleted_count > 0,
                "deleted_count": deleted_count,
                "total_count": total_count,
                "errors": errors,
            }

        except Exception as e:
            # Откатываем изменения в случае ошибки
            await self.session.rollback()
            errors.append(f"Database error: {str(e)}")

            return {
                "success": False,
                "deleted_count": deleted_count,
                "total_count": total_count if "total_count" in locals() else 0,
                "errors": errors,
            }
