"""Репозиторий статистики вопросника."""

import logging
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Stats.questioner import QuestionerChats
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class QuestionerChatsRepo(BaseRepo):
    """Репозиторий для работы со статистикой чатов вопросника."""

    async def add_rows(
        self,
        rows: Sequence[dict[str, Any]],
    ) -> tuple[int, int]:
        """
        Добавить строки статистики.

        Returns:
            tuple:
                inserted_count - сколько строк реально добавлено;
                duplicate_count - сколько строк уже существовало.
        """

        if not rows:
            return 0, 0

        chat_ids = {
            int(row["chat_id"])
            for row in rows
        }

        try:
            existing_query = (
                select(
                    QuestionerChats.chat_id,
                    QuestionerChats.user_id,
                    QuestionerChats.role_user,
                )
                .where(
                    QuestionerChats.chat_id.in_(chat_ids)
                )
            )

            result = await self.session.execute(
                existing_query
            )

            existing_keys = {
                (
                    int(chat_id),
                    int(user_id),
                    str(role_user),
                )
                for chat_id, user_id, role_user
                in result.all()
            }

            objects: list[QuestionerChats] = []
            duplicate_count = 0

            # Заодно защищаемся от дублей
            # внутри самого переданного списка.
            seen_keys = set(existing_keys)

            for row in rows:
                key = (
                    int(row["chat_id"]),
                    int(row["user_id"]),
                    str(row["role_user"]),
                )

                if key in seen_keys:
                    duplicate_count += 1
                    continue

                seen_keys.add(key)

                objects.append(
                    QuestionerChats(
                        uuid=str(row["uuid"]),
                        user_id=int(row["user_id"]),
                        chat_id=int(row["chat_id"]),
                        role_user=str(row["role_user"]),
                        kb_link=row.get("kb_link"),
                        created_at=row["created_at"],
                        closed_at=row["closed_at"],
                        rate=row.get("rate"),
                    )
                )

            if not objects:
                return 0, duplicate_count

            self.session.add_all(objects)
            await self.session.commit()

            return len(objects), duplicate_count

        except SQLAlchemyError:
            await self.session.rollback()

            logger.exception(
                "[БД] Ошибка записи статистики QuestionerChats"
            )

            raise