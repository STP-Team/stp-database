"""Репозитории статистики вопросника."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Stats.questioner import (
    QuestionerChats,
    QuestionerMonth,
)
from stp_database.repo.base import BaseRepo


logger = logging.getLogger(__name__)


class QuestionerChatsRepo(BaseRepo):
    """Репозиторий ежедневной статистики вопросника."""

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
                    QuestionerChats.chat_id.in_(
                        chat_ids
                    )
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

            objects: list[
                QuestionerChats
            ] = []

            duplicate_count = 0

            seen_keys = set(
                existing_keys
            )

            for row in rows:
                key = (
                    int(row["chat_id"]),
                    int(row["user_id"]),
                    str(row["role_user"]),
                )

                if key in seen_keys:
                    duplicate_count += 1
                    continue

                seen_keys.add(
                    key
                )

                objects.append(
                    QuestionerChats(
                        uuid=str(
                            row["uuid"]
                        ),
                        user_id=int(
                            row["user_id"]
                        ),
                        chat_id=int(
                            row["chat_id"]
                        ),
                        role_user=str(
                            row["role_user"]
                        ),
                        kb_link=row.get(
                            "kb_link"
                        ),
                        created_at=row[
                            "created_at"
                        ],
                        closed_at=row[
                            "closed_at"
                        ],
                        rate=row.get(
                            "rate"
                        ),
                    )
                )

            if not objects:
                return (
                    0,
                    duplicate_count,
                )

            self.session.add_all(
                objects
            )

            await self.session.commit()

            return (
                len(objects),
                duplicate_count,
            )

        except SQLAlchemyError:
            await self.session.rollback()

            logger.exception(
                "[БД] Ошибка записи статистики "
                "QuestionerChats"
            )

            raise

    async def get_rows_for_period(
        self,
        period_start: datetime,
        period_end: datetime,
    ):
        """
        Получить QuestionerChats
        за указанный период.

        period_start включительно.
        period_end не включительно.
        """

        try:
            query = (
                select(
                    QuestionerChats.chat_id,
                    QuestionerChats.user_id,
                    QuestionerChats.role_user,
                    QuestionerChats.created_at,
                    QuestionerChats.closed_at,
                    QuestionerChats.rate,
                )
                .where(
                    QuestionerChats.closed_at
                    >= period_start,

                    QuestionerChats.closed_at
                    < period_end,
                )
                .order_by(
                    QuestionerChats.chat_id
                )
            )

            result = await self.session.execute(
                query
            )

            return result.all()

        except SQLAlchemyError:
            logger.exception(
                "[QuestionerChats] "
                "Ошибка получения статистики "
                "за период %s - %s",
                period_start,
                period_end,
            )

            raise


class QuestionerMonthRepo(BaseRepo):
    """Репозиторий месячной статистики вопросника."""

    async def upsert_rows(
        self,
        rows: Sequence[dict[str, Any]],
    ) -> tuple[int, int]:
        """
        Создать или обновить показатели
        в QuestionerMonth.

        employee_id является PK.

        Returns:
            created_count
            updated_count
        """

        if not rows:
            return 0, 0

        employee_ids = {
            int(
                row["employee_id"]
            )
            for row in rows
        }

        try:
            query = (
                select(
                    QuestionerMonth
                )
                .where(
                    QuestionerMonth.employee_id.in_(
                        employee_ids
                    )
                )
            )

            result = await self.session.execute(
                query
            )

            existing_rows = {
                int(row.employee_id): row
                for row
                in result.scalars().all()
            }

            created_count = 0
            updated_count = 0

            now = datetime.now()

            for row in rows:
                employee_id = int(
                    row["employee_id"]
                )

                existing = (
                    existing_rows.get(
                        employee_id
                    )
                )

                if existing is None:
                    self.session.add(
                        QuestionerMonth(
                            employee_id=employee_id,

                            count_questions_asked=int(
                                row[
                                    "count_questions_asked"
                                ]
                            ),

                            count_questions_answered=int(
                                row[
                                    "count_questions_answered"
                                ]
                            ),

                            average_duration_asked_question=float(
                                row[
                                    "average_duration_asked_question"
                                ]
                            ),

                            average_duration_answered_question=float(
                                row[
                                    "average_duration_answered_question"
                                ]
                            ),

                            rate_requester=row.get(
                                "rate_requester"
                            ),

                            rate_responder=row.get(
                                "rate_responder"
                            ),
                        )
                    )

                    created_count += 1

                else:
                    existing.count_questions_asked = int(
                        row[
                            "count_questions_asked"
                        ]
                    )

                    existing.count_questions_answered = int(
                        row[
                            "count_questions_answered"
                        ]
                    )

                    existing.average_duration_asked_question = float(
                        row[
                            "average_duration_asked_question"
                        ]
                    )

                    existing.average_duration_answered_question = float(
                        row[
                            "average_duration_answered_question"
                        ]
                    )

                    existing.rate_requester = row.get(
                        "rate_requester"
                    )

                    existing.rate_responder = row.get(
                        "rate_responder"
                    )

                    existing.updated_at = now

                    updated_count += 1

            await self.session.commit()

            return (
                created_count,
                updated_count,
            )

        except SQLAlchemyError:
            await self.session.rollback()

            logger.exception(
                "[QuestionerMonth] "
                "Ошибка записи месячной статистики"
            )

            raise