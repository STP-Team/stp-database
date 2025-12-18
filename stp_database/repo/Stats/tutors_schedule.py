"""Репозиторий функций для работы с графиком наставников."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Stats.tutors_schedule import TutorsSchedule
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class TutorsScheduleRepo(BaseRepo):
    """Репозиторий с функциями для работы с графиком наставников."""

    async def get_tutor_schedule(
        self,
        tutor_fullname: str | None = None,
        tutor_employee_id: int | None = None,
        extraction_period: datetime | None = None,
    ) -> None | list[Any] | Sequence[TutorsSchedule]:
        """Поиск графика наставника в БД.

        Args:
            tutor_fullname: ФИО наставника
            tutor_employee_id: Идентификатор ОКС наставника
            extraction_period: Дата выгрузки графика

        Returns:
            HeadPremium или ничего (если передана строка)
            Список объектов HeadPremium (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        filters = []

        if tutor_fullname:
            filters.append(TutorsSchedule.tutor_fullname == tutor_fullname)

        if tutor_employee_id:
            filters.append(TutorsSchedule.tutor_employee_id == tutor_employee_id)

        filters.append(TutorsSchedule.extraction_period == extraction_period)

        query = (
            select(TutorsSchedule)
            .where(*filters)
            .where(TutorsSchedule.extraction_period == extraction_period)
            .order_by(TutorsSchedule.training_day.desc())
        )

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения графика наставника: {e}")
            return None

    async def get_trainee_schedule(
        self,
        trainee_fullname: str | None = None,
        trainee_employee_id: int | None = None,
        extraction_period: datetime | None = None,
    ) -> None | list[Any] | Sequence[TutorsSchedule]:
        """Поиск графика стажера в БД.

        Args:
            trainee_fullname: ФИО стажера
            trainee_employee_id: Идентификатор ОКС стажера
            extraction_period: Дата выгрузки графика

        Returns:
            HeadPremium или ничего (если передана строка)
            Список объектов HeadPremium (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        filters = []

        if trainee_fullname:
            filters.append(TutorsSchedule.tutor_fullname == trainee_fullname)

        if trainee_employee_id:
            filters.append(TutorsSchedule.tutor_employee_id == trainee_employee_id)

        filters.append(TutorsSchedule.extraction_period == extraction_period)

        query = (
            select(TutorsSchedule)
            .where(*filters)
            .where(TutorsSchedule.extraction_period == extraction_period)
            .order_by(TutorsSchedule.training_day.desc())
        )

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения графика стажера: {e}")
            return None
