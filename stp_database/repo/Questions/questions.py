"""Репозиторий функций для работы с вопросами."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Sequence

from sqlalchemy import and_, extract, func, or_, select

from stp_database import DbConfig
from stp_database.models.Questions.question import Question
from stp_database.models.STP.employee import Employee
from stp_database.repo.base import BaseRepo


class QuestionsRepo(BaseRepo):
    """Репозиторий с функциями для работы с вопросами."""

    async def add_question(
        self,
        group_id: int,
        topic_id: int,
        employee_userid: int,
        question_text: str,
        start_time: datetime,
        clever_link: str,
        activity_status_enabled: bool | None = None,
    ) -> Question:
        """Добавление нового вопроса.

        Args:
            group_id: Идентификатор группы Telegram, которой принадлежит вопрос
            topic_id: Идентификатор топика Telegram, которому принадлежит вопрос
            employee_userid: Идентификатор Telegram специалиста, задавшего вопрос
            question_text: Текст заданного вопроса
            start_time: Время открытия вопроса
            clever_link: Ссылка на базу знаний от специалиста
            activity_status_enabled: Включено ли отслеживание бездействия

        Returns:
             Объект созданного Question
        """
        token = str(uuid.uuid4())

        question = Question(
            token=token,
            group_id=group_id,
            topic_id=topic_id,
            employee_userid=employee_userid,
            question_text=question_text,
            start_time=start_time,
            clever_link=clever_link,
            status="open",
            allow_return=True,
            activity_status_enabled=activity_status_enabled,
        )

        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)
        return question

    async def update_question(
        self,
        token: str = None,
        group_id: int = None,
        topic_id: int = None,
        **kwargs: Any,
    ) -> Question | None:
        """Обновление вопроса.

        Args:
            token: Токен вопроса
            group_id: Идентификатор группы Telegram
            topic_id: Идентификатор топика группы Telegram
            **kwargs: Параметры для обновления

        Returns:
            Обновленный объект Question или None
        """
        if token:
            select_stmt = select(Question).where(Question.token == token)
        elif group_id and topic_id:
            select_stmt = select(Question).where(
                Question.token == token,
                Question.group_id == group_id,
                Question.topic_id == topic_id,
            )
        else:
            return None

        result = await self.session.execute(select_stmt)
        question = result.scalar_one_or_none()

        # Если вопрос существует - обновляем его
        if question:
            for key, value in kwargs.items():
                setattr(question, key, value)
            await self.session.commit()

        return question

    async def get_question(
        self, token: str = None, group_id: str | int = None, topic_id: int = None
    ) -> Question | None:
        """Получение вопроса по токену или идентификатору топика.

        Args:
            token: Токен вопроса
            group_id: Идентификатор группы в Telegram
            topic_id: Идентификатор топика в Telegram

        Returns:
            Объект Question найденного вопроса или None
        """
        if token:
            stmt = select(Question).where(Question.token == token)
        else:
            stmt = select(Question).where(
                Question.topic_id == topic_id, Question.group_id == group_id
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_questions(self) -> Sequence[Question]:
        """Получение текущих активных вопросов.

        Активным вопросом считается вопрос, имеющий статус open или in_progress

        Returns:
             Последовательность активных вопросов Question
        """
        stmt = select(Question).where(
            or_(Question.status == "open", Question.status == "in_progress")
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_questions_by_month(self, month: int, year: int) -> Sequence[Question]:
        """Получение вопросов за указанный месяц.

        Args:
            month: Фильтр по месяцу
            year: Фильтр по году

        Returns:
             Последовательность отфильтрованных вопросов
        """
        stmt = select(Question).where(
            extract("month", Question.start_time) == month,
            extract("year", Question.start_time) == year,
        )

        result = await self.session.execute(stmt)
        questions = result.scalars().all()

        return questions

    async def get_questions_count_today(
        self, employee_userid: int | None = None, duty_userid: int | None = None
    ) -> int:
        """Получение кол-ва вопросов специалиста за последний день.

        Может использоваться как для поиска вопросов специалиста, так и для вопросов дежурного

        Args:
            employee_userid: Идентификатор Telegram искомого специалиста
            duty_userid: Идентификатор Telegram искомого дежурного

        Returns:
            Кол-во вопросов за последний день
        """
        today = datetime.now(tz=DbConfig.tz).date()
        tomorrow = today + timedelta(days=1)

        if employee_userid:
            stmt = select(func.count(Question.token)).where(
                and_(
                    Question.employee_userid == employee_userid,
                    Question.start_time >= today,
                    Question.start_time < tomorrow,
                )
            )
        else:
            stmt = select(func.count(Question.token)).where(
                and_(
                    Question.duty_userid == duty_userid,
                    Question.start_time >= today,
                    Question.start_time < tomorrow,
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_questions_count_last_month(
        self, employee_userid: int | None = None, duty_userid: int | None = None
    ) -> int:
        """Получение кол-ва вопросов специалиста за последний месяц.

        Может использоваться как для поиска вопросов специалиста, так и для вопросов дежурного

        Args:
            employee_userid: Идентификатор Telegram искомого специалиста
            duty_userid: Идентификатор Telegram искомого дежурного

        Returns:
            Кол-во вопросов за последний месяц
        """
        today = datetime.now(tz=DbConfig.tz)
        first_day_current_month = datetime(today.year, today.month, 1).date()

        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        first_day_next_month = datetime(next_year, next_month, 1).date()

        if employee_userid:
            stmt = select(func.count(Question.token)).where(
                and_(
                    Question.employee_userid == employee_userid,
                    Question.start_time >= first_day_current_month,
                    Question.start_time < first_day_next_month,
                )
            )
        else:
            stmt = select(func.count(Question.token)).where(
                and_(
                    Question.duty_userid == duty_userid,
                    Question.start_time >= first_day_current_month,
                    Question.start_time < first_day_next_month,
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_last_questions_by_chat_id(
        self, employee_chat_id: int, limit: int = 5
    ) -> Sequence[Question]:
        """Получение последних N вопросов специалиста.

        Args:
            employee_chat_id: Идентификатор специалиста Telegram
            limit: Лимит вопросов для выдачи. Сортировка по убыванию даты закрытия вопроса

        Returns:
            Последовательность вопросов
        """
        twenty_four_hours_ago = datetime.now(tz=DbConfig.tz) - timedelta(hours=24)

        stmt = (
            select(Question)
            .where(
                and_(
                    Question.employee_userid == employee_chat_id,
                    Question.question_text.is_not(None),
                    Question.status == "closed",
                    Question.end_time.is_not(None),
                    Question.end_time >= twenty_four_hours_ago,
                    Question.allow_return,
                )
            )
            .order_by(Question.end_time.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_available_to_return_questions(self) -> Sequence[Question]:
        """Получение доступных к возврату вопросов.

        Returns:
            Последовательность доступных к возврату вопросов
        """
        twenty_four_hours_ago = datetime.now(tz=DbConfig.tz) - timedelta(hours=24)

        stmt = (
            select(Question)
            .where(
                and_(
                    Question.question_text.is_not(None),
                    Question.status == "closed",
                    Question.end_time.is_not(None),
                    Question.end_time >= twenty_four_hours_ago,
                    Question.allow_return,
                )
            )
            .order_by(Question.end_time.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_users_by_division(
        self, division: str, main_repo, limit: int = 15
    ) -> Sequence[Employee]:
        """Получение топ-15 пользователей по количеству вопросов в рамках указанного направления.

        Args:
            division: Направление для фильтрации (НЦК/НТП)
            main_repo: Репозиторий для работы с основной БД
            limit: Лимит пользователей для возврата

        Returns:
            Последовательность из топ-15 пользователей с наибольшим количеством вопросов
        """
        # Получаем все вопросы
        stmt = select(Question)
        result = await self.session.execute(stmt)
        questions = result.scalars().all()

        # Словарь для подсчета вопросов по пользователям
        user_question_counts = {}
        processed_users = {}  # Кеш для пользователей, чтобы не запрашивать их повторно

        for question in questions:
            try:
                # Проверяем, есть ли пользователь в кеше
                if question.employee_userid not in processed_users:
                    user: Employee = await main_repo.employee.get_user(
                        user_id=question.employee_userid
                    )
                    processed_users[question.employee_userid] = user
                else:
                    user: Employee = processed_users[question.employee_userid]

                # Фильтруем по направлению
                if user and division.upper() in user.division.upper():
                    if user.fullname not in user_question_counts:
                        user_question_counts[user.fullname] = {
                            "user": Employee,
                            "count": 0,
                        }
                    user_question_counts[user.fullname]["count"] += 1

            except Exception:
                continue

        # Сортируем пользователей по количеству вопросов (по убыванию) и берем топ-15
        sorted_users = sorted(
            user_question_counts.values(), key=lambda x: x["count"], reverse=True
        )[:limit]

        # Возвращаем только объекты User
        return [user_data["user"] for user_data in sorted_users]

    async def get_old_questions(self, days: int) -> Sequence[Question]:
        """Получение старых вопросов.

        Args:
            days: Кол-во дней от текущего дня

        Returns:
             Последовательность вопросов старше определенной даты
        """
        today = datetime.now(tz=DbConfig.tz)
        old_date = today - timedelta(days=days)

        stmt = select(Question).where(Question.start_time < old_date)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_questions(
        self,
        token: str = None,
        group_id: int = None,
        topic_id: int = None,
        duty_userid: int = None,
        employee_userid: int = None,
        question_text: str = None,
        start_time_from: datetime = None,
        start_time_to: datetime = None,
        end_time_from: datetime = None,
        end_time_to: datetime = None,
        clever_link: str = None,
        quality_duty: bool = None,
        quality_employee: bool = None,
        status: str | list[str] = None,
        allow_return: bool = None,
        activity_status_enabled: bool = None,
        limit: int = None,
        offset: int = None,
        order_by: str = "start_time",
        order_direction: str = "desc",
    ) -> Sequence[Question]:
        """Получение вопросов с фильтрацией по всем доступным параметрам.

        Args:
            token: Уникальный токен вопроса
            group_id: Идентификатор Telegram группы
            topic_id: Идентификатор Telegram темы в группе
            duty_userid: Идентификатор Telegram дежурного
            employee_userid: Идентификатор Telegram сотрудника
            question_text: Поиск по тексту вопроса (содержит)
            start_time_from: Начальная дата для фильтрации по времени начала
            start_time_to: Конечная дата для фильтрации по времени начала
            end_time_from: Начальная дата для фильтрации по времени окончания
            end_time_to: Конечная дата для фильтрации по времени окончания
            clever_link: Поиск по ссылке на Clever (содержит)
            quality_duty: Оценка качества дежурного
            quality_employee: Оценка качества сотрудника
            status: Статус вопроса (строка или список строк)
            allow_return: Разрешен ли возврат
            activity_status_enabled: Включен ли статус активности
            limit: Лимит количества результатов
            offset: Смещение для пагинации
            order_by: Поле для сортировки (start_time, end_time, token, status)
            order_direction: Направление сортировки (asc, desc)

        Returns:
            Последовательность отфильтрованных вопросов Question
        """
        stmt = select(Question)
        conditions = []

        # Фильтрация по токену
        if token:
            conditions.append(Question.token == token)

        # Фильтрация по идентификаторам
        if group_id is not None:
            conditions.append(Question.group_id == group_id)
        if topic_id is not None:
            conditions.append(Question.topic_id == topic_id)
        if duty_userid is not None:
            conditions.append(Question.duty_userid == duty_userid)
        if employee_userid is not None:
            conditions.append(Question.employee_userid == employee_userid)

        # Поиск по тексту вопроса
        if question_text:
            conditions.append(Question.question_text.ilike(f"%{question_text}%"))

        # Фильтрация по диапазону времени начала
        if start_time_from:
            conditions.append(Question.start_time >= start_time_from)
        if start_time_to:
            conditions.append(Question.start_time <= start_time_to)

        # Фильтрация по диапазону времени окончания
        if end_time_from:
            conditions.append(Question.end_time >= end_time_from)
        if end_time_to:
            conditions.append(Question.end_time <= end_time_to)

        # Поиск по ссылке на Clever
        if clever_link:
            conditions.append(Question.clever_link.ilike(f"%{clever_link}%"))

        # Фильтрация по качеству
        if quality_duty is not None:
            conditions.append(Question.quality_duty == quality_duty)
        if quality_employee is not None:
            conditions.append(Question.quality_employee == quality_employee)

        # Фильтрация по статусу
        if status is not None:
            if isinstance(status, list):
                conditions.append(Question.status.in_(status))
            else:
                conditions.append(Question.status == status)

        # Фильтрация по булевым полям
        if allow_return is not None:
            conditions.append(Question.allow_return == allow_return)
        if activity_status_enabled is not None:
            conditions.append(
                Question.activity_status_enabled == activity_status_enabled
            )

        # Применение условий
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Сортировка
        order_column = getattr(Question, order_by, Question.start_time)
        if order_direction.lower() == "desc":
            stmt = stmt.order_by(order_column.desc())
        else:
            stmt = stmt.order_by(order_column.asc())

        # Лимит и смещение
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_question(
        self, token: str = None, questions: Sequence[Question] = None
    ) -> dict:
        """Удаление вопроса из БД.

        Удаляет либо вопрос по его токену, либо список вопросов, переданный в questions

        Args:
            token: Уникальный идентификатор вопроса
            questions: Последовательность вопросов на удаление

        Returns:
            Словарь с результатом удаления
        """
        if token is None and questions is None:
            return {
                "success": False,
                "deleted_count": 0,
                "total_count": 0,
                "errors": ["Either token or questions must be provided"],
            }

        deleted_count = 0
        total_count = 0
        errors = []

        try:
            if token:
                question = await self.session.get(Question, token)
                if question is None:
                    return {
                        "success": False,
                        "deleted_count": 0,
                        "total_count": 1,
                        "errors": [f"Question with token {token} not found"],
                    }
                await self.session.delete(question)
                deleted_count = 1
                total_count = 1
            else:
                total_count = len(questions)
                for question in questions:
                    try:
                        await self.session.refresh(question)
                        await self.session.delete(question)
                        deleted_count += 1
                    except Exception as e:
                        errors.append(
                            f"Error deleting question {question.token}: {str(e)}"
                        )

            await self.session.commit()

            return {
                "success": deleted_count > 0,
                "deleted_count": deleted_count,
                "total_count": total_count,
                "errors": errors,
            }

        except Exception as e:
            await self.session.rollback()
            errors.append(f"Database error: {str(e)}")
            return {
                "success": False,
                "deleted_count": deleted_count,
                "total_count": total_count if "total_count" in locals() else 0,
                "errors": errors,
            }
