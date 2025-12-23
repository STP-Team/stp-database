"""Репозиторий функций для взаимодействия с назначенными тестами."""

import logging
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.Stats.tests import AssignedTest
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class AssignedTestRepo(BaseRepo):
    """Репозиторий для работы с назначенными тестами."""

    async def add_test(
        self,
        test_name: str,
        employee_fullname: str,
        active_from: datetime,
        head_fullname: str | None = None,
        creator_fullname: str | None = None,
        status: str | None = None,
        extraction_period: datetime | None = None,
    ) -> AssignedTest | None:
        """Добавление нового назначенного теста.

        Args:
            test_name: Название теста
            employee_fullname: ФИО сотрудника, кому назначен тест
            active_from: Дата назначения теста
            head_fullname: ФИО руководителя сотрудника
            creator_fullname: ФИО создателя теста
            status: Статус теста
            extraction_period: Дата начала периода выгрузки

        Returns:
            Созданный объект AssignedTest или None в случае ошибки
        """
        new_test = AssignedTest(
            test_name=test_name,
            employee_fullname=employee_fullname,
            head_fullname=head_fullname,
            creator_fullname=creator_fullname,
            status=status,
            active_from=active_from,
            extraction_period=extraction_period,
            created_at=datetime.now(),
        )

        try:
            self.session.add(new_test)
            await self.session.commit()
            await self.session.refresh(new_test)
            logger.info(
                f"[БД] Создан новый назначенный тест: {test_name} для {employee_fullname}"
            )
            return new_test
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка добавления назначенного теста {test_name}: {e}")
            await self.session.rollback()
            return None

    async def get_tests(
        self,
        test_id: int | list[int] | None = None,
        test_name: str | None = None,
        employee_fullname: str | list[str] | None = None,
        head_fullname: str | list[str] | None = None,
        creator_fullname: str | None = None,
        status: str | list[str] | None = None,
        active_from_start: datetime | None = None,
        active_from_end: datetime | None = None,
        limit: int | None = None,
    ) -> AssignedTest | None | Sequence[AssignedTest]:
        """Поиск назначенного теста или списка назначенных тестов.

        Args:
            test_id: ID теста (int - возвращает один тест, list[int] - возвращает список)
            test_name: Название теста (если указано, возвращает один тест)
            employee_fullname: ФИО сотрудника (str - один, list[str] - список)
            head_fullname: ФИО руководителя (str - один, list[str] - список)
            creator_fullname: ФИО создателя теста
            status: Статус теста (str - один, list[str] - список)
            active_from_start: Начальная дата периода назначения
            active_from_end: Конечная дата периода назначения
            limit: Максимальное количество результатов

        Returns:
            Объект AssignedTest или None (если указан одиночный параметр)
            Последовательность AssignedTest (если указаны списки или множественные критерии)
        """
        # Определяем, одиночный запрос или множественный
        is_single = (isinstance(test_id, int)) or (
            test_name is not None and isinstance(employee_fullname, str)
        )

        if is_single:
            # Запрос одного теста
            filters = []

            if isinstance(test_id, int):
                filters.append(AssignedTest.id == test_id)
            if test_name and isinstance(employee_fullname, str):
                filters.append(
                    and_(
                        AssignedTest.test_name == test_name,
                        AssignedTest.employee_fullname == employee_fullname,
                    )
                )

            query = (
                select(AssignedTest)
                .where(*filters)
                .order_by(AssignedTest.active_from.desc())
            )

            try:
                result = await self.session.execute(query)
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка получения назначенного теста: {e}")
                return None
        else:
            # Запрос списка тестов
            filters = []

            # Фильтр по test_id (список)
            if isinstance(test_id, list) and test_id:
                filters.append(AssignedTest.id.in_(test_id))

            # Фильтр по названию теста
            if test_name:
                filters.append(AssignedTest.test_name.ilike(f"%{test_name}%"))

            # Фильтр по сотрудникам
            if employee_fullname is not None:
                if isinstance(employee_fullname, str):
                    filters.append(AssignedTest.employee_fullname == employee_fullname)
                elif isinstance(employee_fullname, list) and employee_fullname:
                    filters.append(
                        AssignedTest.employee_fullname.in_(employee_fullname)
                    )

            # Фильтр по руководителям
            if head_fullname is not None:
                if isinstance(head_fullname, str):
                    filters.append(AssignedTest.head_fullname == head_fullname)
                elif isinstance(head_fullname, list) and head_fullname:
                    filters.append(AssignedTest.head_fullname.in_(head_fullname))

            # Фильтр по создателю
            if creator_fullname is not None:
                filters.append(AssignedTest.creator_fullname == creator_fullname)

            # Фильтр по статусу
            if status is not None:
                if isinstance(status, str):
                    filters.append(AssignedTest.status == status)
                elif isinstance(status, list) and status:
                    filters.append(AssignedTest.status.in_(status))

            # Фильтр по периоду назначения
            if active_from_start:
                filters.append(AssignedTest.active_from >= active_from_start)
            if active_from_end:
                filters.append(AssignedTest.active_from <= active_from_end)

            # Формируем запрос
            if filters:
                query = (
                    select(AssignedTest)
                    .where(*filters)
                    .order_by(AssignedTest.active_from.desc())
                )
            else:
                # Все тесты
                query = select(AssignedTest).order_by(AssignedTest.active_from.desc())

            if limit:
                query = query.limit(limit)

            try:
                result = await self.session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                logger.error(f"[БД] Ошибка получения списка назначенных тестов: {e}")
                return []

    async def get_tests_by_employee(
        self, employee_fullname: str, limit: int = None
    ) -> Sequence[AssignedTest]:
        """Получение всех тестов для конкретного сотрудника.

        Args:
            employee_fullname: ФИО сотрудника
            limit: Максимальное количество результатов

        Returns:
            Список назначенных тестов для сотрудника
        """
        query = (
            select(AssignedTest)
            .where(AssignedTest.employee_fullname == employee_fullname)
            .order_by(AssignedTest.active_from.desc())
        )

        if limit:
            query = query.limit(limit)

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения тестов для сотрудника {employee_fullname}: {e}"
            )
            return []

    async def get_tests_by_status(
        self, status: str, limit: int = None
    ) -> Sequence[AssignedTest]:
        """Получение всех тестов с определенным статусом.

        Args:
            status: Статус теста
            limit: Максимальное количество результатов

        Returns:
            Список назначенных тестов с указанным статусом
        """
        query = (
            select(AssignedTest)
            .where(AssignedTest.status == status)
            .order_by(AssignedTest.active_from.desc())
        )

        if limit:
            query = query.limit(limit)

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения тестов со статусом {status}: {e}")
            return []

    async def get_tests_by_head(
        self, head_fullname: str, limit: int = None
    ) -> Sequence[AssignedTest]:
        """Получение всех тестов для команды руководителя.

        Args:
            head_fullname: ФИО руководителя
            limit: Максимальное количество результатов

        Returns:
            Список назначенных тестов для команды руководителя
        """
        query = (
            select(AssignedTest)
            .where(AssignedTest.head_fullname == head_fullname)
            .order_by(AssignedTest.active_from.desc())
        )

        if limit:
            query = query.limit(limit)

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения тестов для команды {head_fullname}: {e}"
            )
            return []

    async def get_tests_for_period(
        self, start_date: datetime, end_date: datetime, limit: int = None
    ) -> Sequence[AssignedTest]:
        """Получение всех тестов, назначенных в определенный период.

        Args:
            start_date: Начальная дата периода
            end_date: Конечная дата периода
            limit: Максимальное количество результатов

        Returns:
            Список назначенных тестов за период
        """
        query = (
            select(AssignedTest)
            .where(
                and_(
                    AssignedTest.active_from >= start_date,
                    AssignedTest.active_from <= end_date,
                )
            )
            .order_by(AssignedTest.active_from.desc())
        )

        if limit:
            query = query.limit(limit)

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка получения тестов за период {start_date} - {end_date}: {e}"
            )
            return []

    async def search_tests(
        self, search_query: str, limit: int = 50
    ) -> Sequence[AssignedTest]:
        """Универсальный поиск назначенных тестов.

        Поиск по различным критериям:
        - Название теста
        - ФИО сотрудника
        - ФИО руководителя
        - ФИО создателя
        - Статус

        Args:
            search_query: Поисковый запрос
            limit: Максимальное количество результатов

        Returns:
            Список найденных назначенных тестов
        """
        search_query = search_query.strip()
        if not search_query:
            return []

        conditions = [
            AssignedTest.test_name.ilike(f"%{search_query}%"),
            AssignedTest.employee_fullname.ilike(f"%{search_query}%"),
            AssignedTest.head_fullname.ilike(f"%{search_query}%"),
            AssignedTest.creator_fullname.ilike(f"%{search_query}%"),
            AssignedTest.status.ilike(f"%{search_query}%"),
        ]

        query = (
            select(AssignedTest)
            .where(or_(*conditions))
            .order_by(AssignedTest.active_from.desc())
            .limit(limit)
        )

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка универсального поиска назначенных тестов: {e}")
            return []

    async def update_test(
        self,
        test_id: int,
        **kwargs: Any,
    ) -> AssignedTest | None:
        """Обновление назначенного теста.

        Args:
            test_id: ID теста для обновления
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект AssignedTest или None
        """
        select_stmt = select(AssignedTest).where(AssignedTest.id == test_id)

        try:
            result = await self.session.execute(select_stmt)
            test: AssignedTest | None = result.scalar_one_or_none()

            # Если тест существует - обновляем его
            if test:
                for key, value in kwargs.items():
                    if hasattr(test, key):
                        setattr(test, key, value)
                await self.session.commit()
                await self.session.refresh(test)
                logger.info(f"[БД] Обновлен тест ID {test_id}")

            return test
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка обновления теста ID {test_id}: {e}")
            await self.session.rollback()
            return None

    async def update_test_status(
        self, test_id: int, status: str
    ) -> AssignedTest | None:
        """Обновление статуса назначенного теста.

        Args:
            test_id: ID теста
            status: Новый статус

        Returns:
            Обновленный объект AssignedTest или None
        """
        return await self.update_test(test_id, status=status)

    async def delete_test(self, test_id: int) -> bool:
        """Удаление назначенного теста.

        Args:
            test_id: ID теста для удаления

        Returns:
            True если тест был удален, False в противном случае
        """
        try:
            # Находим тест
            select_stmt = select(AssignedTest).where(AssignedTest.id == test_id)
            result = await self.session.execute(select_stmt)
            test: AssignedTest | None = result.scalar_one_or_none()

            if test:
                await self.session.delete(test)
                await self.session.commit()
                logger.info(f"[БД] Тест ID {test_id} удален из базы")
                return True
            else:
                logger.warning(f"[БД] Тест с ID {test_id} не найден для удаления")
                return False
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка удаления теста ID {test_id}: {e}")
            await self.session.rollback()
            return False

    async def delete_tests_by_employee(self, employee_fullname: str) -> int:
        """Удаление всех тестов для конкретного сотрудника.

        Args:
            employee_fullname: ФИО сотрудника

        Returns:
            Количество удаленных тестов
        """
        try:
            # Находим все тесты сотрудника
            query = select(AssignedTest).where(
                AssignedTest.employee_fullname == employee_fullname
            )
            result = await self.session.execute(query)
            tests = result.scalars().all()

            deleted_count = 0
            for test in tests:
                await self.session.delete(test)
                deleted_count += 1

            if deleted_count > 0:
                await self.session.commit()
                logger.info(
                    f"[БД] Удалено {deleted_count} тестов для сотрудника {employee_fullname}"
                )

            return deleted_count
        except SQLAlchemyError as e:
            logger.error(
                f"[БД] Ошибка удаления тестов для сотрудника {employee_fullname}: {e}"
            )
            await self.session.rollback()
            return 0

    async def get_statistics(self) -> dict:
        """Получение статистики по назначенным тестам.

        Returns:
            Словарь со статистикой тестов
        """
        try:
            # Общее количество тестов
            total_query = select(AssignedTest)
            total_result = await self.session.execute(total_query)
            total_tests = len(total_result.scalars().all())

            # Статистика по статусам
            status_stats = {}
            if total_tests > 0:
                # Получаем все уникальные статусы
                status_query = select(AssignedTest.status).distinct()
                status_result = await self.session.execute(status_query)
                statuses = [s[0] for s in status_result.fetchall() if s[0]]

                # Подсчитываем количество для каждого статуса
                for status in statuses:
                    status_count_query = select(AssignedTest).where(
                        AssignedTest.status == status
                    )
                    status_count_result = await self.session.execute(status_count_query)
                    status_stats[status] = len(status_count_result.scalars().all())

            return {
                "total_tests": total_tests,
                "status_statistics": status_stats,
            }
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения статистики тестов: {e}")
            return {"total_tests": 0, "status_statistics": {}}
