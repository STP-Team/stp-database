"""Репозиторий функций для работы с графиком наставников."""

import logging
from datetime import date, datetime
from typing import Any, Sequence

from sqlalchemy import and_, func, select
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
        division: str | None = None,
    ) -> None | list[Any] | Sequence[TutorsSchedule]:
        """Поиск графика наставника в БД.

        Args:
            tutor_fullname: ФИО наставника
            tutor_employee_id: Идентификатор ОКС наставника
            extraction_period: Дата выгрузки графика
            division: Подразделение наставника (НТП1, НТП2, НЦК)

        Returns:
            TutorsSchedule или ничего (если передана строка)
            Список объектов TutorsSchedule (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        filters = []

        if tutor_fullname:
            filters.append(TutorsSchedule.tutor_fullname == tutor_fullname)

        if tutor_employee_id:
            filters.append(TutorsSchedule.tutor_employee_id == tutor_employee_id)

        if extraction_period:
            filters.append(TutorsSchedule.extraction_period == extraction_period)

        if division:
            # Специальная обработка для НЦК -> НТП НЦК
            division_value = "НТП НЦК" if division == "НЦК" else division
            filters.append(TutorsSchedule.tutor_division == division_value)

        query = (
            select(TutorsSchedule)
            .where(*filters)
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
        division: str | None = None,
    ) -> None | list[Any] | Sequence[TutorsSchedule]:
        """Поиск графика стажера в БД.

        Args:
            trainee_fullname: ФИО стажера
            trainee_employee_id: Идентификатор ОКС стажера
            extraction_period: Дата выгрузки графика
            division: Подразделение наставника (НТП1, НТП2, НЦК)

        Returns:
            TutorsSchedule или ничего (если передана строка)
            Список объектов TutorsSchedule (если передан список)
        """
        # Определяем, одиночный запрос или множественный
        filters = []

        if trainee_fullname:
            filters.append(TutorsSchedule.trainee_fullname == trainee_fullname)

        if trainee_employee_id:
            filters.append(TutorsSchedule.trainee_employee_id == trainee_employee_id)

        if extraction_period:
            filters.append(TutorsSchedule.extraction_period == extraction_period)

        if division:
            # Специальная обработка для НЦК -> НТП НЦК
            division_value = "НТП НЦК" if division == "НЦК" else division
            filters.append(TutorsSchedule.tutor_division == division_value)

        query = (
            select(TutorsSchedule)
            .where(*filters)
            .order_by(TutorsSchedule.training_day.desc())
        )

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения графика стажера: {e}")
            return None

    async def get_tutor_trainees_by_date_range(
        self,
        start_date: date,
        end_date: date,
        tutor_fullname: str | None = None,
        tutor_employee_id: int | None = None,
        extraction_period: datetime | None = None,
        division: str | None = None,
    ) -> Sequence[TutorsSchedule]:
        """Получить всех стажеров наставника за период.

        Args:
            tutor_fullname: ФИО наставника
            tutor_employee_id: ID наставника
            start_date: Начальная дата
            end_date: Конечная дата
            extraction_period: Период выгрузки
            division: Подразделение наставника (НТП1, НТП2, НЦК)

        Returns:
            Список записей расписания за указанный период
        """
        query = select(TutorsSchedule).where(
            and_(
                func.date(TutorsSchedule.training_day) >= start_date,
                func.date(TutorsSchedule.training_day) <= end_date,
            )
        )

        if tutor_fullname:
            query = query.where(TutorsSchedule.tutor_fullname == tutor_fullname)
        elif tutor_employee_id:
            query = query.where(TutorsSchedule.tutor_employee_id == tutor_employee_id)

        if extraction_period:
            query = query.where(TutorsSchedule.extraction_period == extraction_period)
        else:
            query = query.where(
                TutorsSchedule.extraction_period
                == (
                    select(func.max(TutorsSchedule.extraction_period)).scalar_subquery()
                )
            )

        if division:
            # Специальная обработка для НЦК -> НТП НЦК
            division_value = "НТП НЦК" if division == "НЦК" else division
            query = query.where(TutorsSchedule.tutor_division == division_value)

        query = query.order_by(
            TutorsSchedule.training_day, TutorsSchedule.training_start_time
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_training_by_date(
        self,
        training_date: date,
        extraction_period: datetime | None = None,
        division: str | None = None,
    ) -> Sequence[TutorsSchedule]:
        """Получить все тренинги на конкретную дату (все наставники и стажеры).

        Args:
            training_date: Дата обучения
            extraction_period: Период выгрузки
            division: Подразделение наставника (НТП1, НТП2, НЦК)

        Returns:
            Список всех записей расписания для указанной даты
        """
        query = select(TutorsSchedule).where(
            func.date(TutorsSchedule.training_day) == training_date
        )

        if extraction_period:
            query = query.where(TutorsSchedule.extraction_period == extraction_period)
        else:
            # Берем последний период выгрузки
            query = query.where(
                TutorsSchedule.extraction_period
                == (
                    select(func.max(TutorsSchedule.extraction_period)).scalar_subquery()
                )
            )

        if division:
            # Специальная обработка для НЦК -> НТП НЦК
            division_value = "НТП НЦК" if division == "НЦК" else division
            query = query.where(TutorsSchedule.tutor_division == division_value)

        query = query.order_by(
            TutorsSchedule.tutor_fullname, TutorsSchedule.training_start_time
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_tutor_trainees_by_date(
        self,
        training_date: date,
        tutor_fullname: str | None = None,
        tutor_employee_id: int | None = None,
        division: str | None = None,
        extraction_period: datetime | None = None,
    ) -> Sequence[TutorsSchedule]:
        """Получить всех стажеров наставника на конкретную дату.

        Args:
            tutor_fullname: ФИО наставника
            tutor_employee_id: ID наставника
            training_date: Дата обучения
            division: Подразделение наставника (НТП1, НТП2, НЦК)
            extraction_period: Период выгрузки

        Returns:
            Список записей расписания для указанной даты
        """
        query = select(TutorsSchedule).where(
            func.date(TutorsSchedule.training_day) == training_date
        )

        if tutor_fullname:
            query = query.where(TutorsSchedule.tutor_fullname == tutor_fullname)
        elif tutor_employee_id:
            query = query.where(TutorsSchedule.tutor_employee_id == tutor_employee_id)

        if division:
            # Специальная обработка для НЦК -> НТП НЦК
            division_value = "НТП НЦК" if division == "НЦК" else division
            query = query.where(TutorsSchedule.tutor_division == division_value)

        if extraction_period:
            query = query.where(TutorsSchedule.extraction_period == extraction_period)
        else:
            # Берем последний период выгрузки
            query = query.where(
                TutorsSchedule.extraction_period
                == (
                    select(func.max(TutorsSchedule.extraction_period)).scalar_subquery()
                )
            )

        query = query.order_by(TutorsSchedule.training_start_time)

        result = await self.session.execute(query)
        return result.scalars().all()
