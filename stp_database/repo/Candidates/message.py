"""Репозиторий сообщений кандидатов."""

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Candidates import Message
from stp_database.repo.base import BaseRepo


logger = logging.getLogger(__name__)


class MessageRepo(BaseRepo):
    """Репозиторий сообщений кандидатов."""

    async def create_message(
        self,
        uuid: str,
        candidate_uuid: str,
        sender_id: int,
        content: str,
        meta: str = "{}",
    ) -> Message | None:
        message = Message(
            uuid=uuid,
            candidate_uuid=candidate_uuid,
            sender_id=sender_id,
            content=content,
            meta=meta,
        )

        try:
            self.session.add(message)
            await self.session.commit()
            await self.session.refresh(message)

            return message

        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка создания сообщения "
                f"{uuid}: {e}"
            )
            await self.session.rollback()
            return None

    async def get_message(
        self,
        uuid: str,
    ) -> Message | None:
        query = select(Message).where(
            Message.uuid == uuid,
        )

        try:
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения сообщения "
                f"{uuid}: {e}"
            )
            return None

    async def get_messages(
        self,
        candidate_uuid: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Message]:
        query = (
            select(Message)
            .where(
                Message.candidate_uuid
                == candidate_uuid
            )
            .order_by(Message.sended_at.asc())
            .offset(offset)
            .limit(limit)
        )

        try:
            result = await self.session.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения сообщений "
                f"кандидата {candidate_uuid}: {e}"
            )
            return []

    async def delete_message(
        self,
        uuid: str,
    ) -> bool:
        message = await self.get_message(uuid)

        if message is None:
            return False

        try:
            await self.session.delete(message)
            await self.session.commit()

            return True

        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка удаления сообщения "
                f"{uuid}: {e}"
            )
            await self.session.rollback()
            return False