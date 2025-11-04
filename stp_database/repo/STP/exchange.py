"""Репозиторий функций для взаимодействия с биржей смен."""

import logging
from datetime import date, datetime, time
from typing import Any, List, Optional, Sequence

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.employee import Employee
from stp_database.models.STP.exchange import (
    Exchange,
    ExchangeSubscription,
    SubscriptionNotification,
)
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class ExchangeRepo(BaseRepo):
    """Репозиторий для работы с биржей смен."""

    async def create_exchange(
        self,
        owner_id: int,
        start_time: Optional[datetime],
        price: int,
        owner_intent: str = "sell",
        end_time: Optional[datetime] = None,
        comment: Optional[str] = None,
        is_private: bool = False,
        payment_type: str = "immediate",
        payment_date: Optional[datetime] = None,
    ) -> Exchange | None:
        """Создание нового сделки смены.

        Args:
            owner_id: Идентификатор владельца объявления (кто создает сделку)
            start_time: Начало смены
            price: Цена за смену
            owner_intent: Намерение владельца ('sell' или 'buy')
            end_time: Окончание смены (если частичная смена)
            comment: Комментарий к сделке
            is_private: Приватный ли сделка
            payment_type: Тип оплаты ('immediate' или 'on_date')
            payment_date: Дата оплаты (если payment_type == 'on_date')

        Returns:
            Созданный объект Exchange или None в случае ошибки
        """
        # Проверяем, что пользователь не забанен
        if await self.is_user_exchange_banned(owner_id):
            logger.warning(f"[Биржа] Пользователь {owner_id} забанен на бирже")
            return None

        new_exchange = Exchange(
            owner_id=owner_id,
            counterpart_id=None,  # Изначально нет второй стороны
            start_time=start_time,
            end_time=end_time,
            price=price,
            owner_intent=owner_intent,
            comment=comment,
            is_private=is_private,
            payment_type=payment_type,
            payment_date=payment_date,
        )

        try:
            self.session.add(new_exchange)
            await self.session.commit()
            await self.session.refresh(new_exchange)
            logger.info(
                f"[Биржа] Создан новый сделка: {new_exchange.id} от владельца {owner_id} ({owner_intent})"
            )
            return new_exchange
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка создания сделки: {e}")
            await self.session.rollback()
            return None

    async def activate_exchange(self, exchange_id: int):
        """Активация подмены.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если сделка успешно активирована, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.status = "active"
            await self.session.commit()
            logger.info(f"[Биржа] Сделка {exchange_id} активирована")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка активации сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def inactivate_exchange(self, exchange_id: int):
        """Деактивация подмены.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если сделка успешно деактивирована, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.status = "inactive"
            await self.session.commit()
            logger.info(f"[Биржа] Сделка {exchange_id} деактивирована")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка деактивации сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def set_private(self, exchange_id: int):
        """Установка приватности предложения.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если предложение успешно запривачено, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.is_private = True
            await self.session.commit()
            logger.info(f"[Биржа] Предложение {exchange_id} запривачено")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка привата предложения {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def set_public(self, exchange_id: int):
        """Установка публичности предложения.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если предложение успешно распривачено, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.is_private = False
            await self.session.commit()
            logger.info(f"[Биржа] Предложение {exchange_id} опубликовано")
            return True
        except SQLAlchemyError as e:
            logger.error(
                f"[Биржа] Ошибка изменения публичности предложения {exchange_id}: {e}"
            )
            await self.session.rollback()
            return False

    async def expire_exchange(self, exchange_id: int) -> bool:
        """Истечение подмены.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если сделка успешно скрыт, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.status = "expired"
            await self.session.commit()
            logger.info(f"[Биржа] Сделка {exchange_id} истечена")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка истечения сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def cancel_exchange(self, exchange_id: int) -> bool:
        """Отмена сделки.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если сделка успешно отменен, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.status = "canceled"
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка отмены сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def delete_exchange(self, exchange_id: int):
        """Удаление сделки.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если сделка успешно отменен, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена.")
                return False

            await self.session.delete(exchange)
            await self.session.commit()
            return True

        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка удаления сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def accept_exchange(
        self, exchange_id: int, counterpart_id: int, mark_as_paid: bool = False
    ) -> Exchange | None:
        """Принятие сделки второй стороной.

        Args:
            exchange_id: Идентификатор сделки
            counterpart_id: Идентификатор принимающей стороны
            mark_as_paid: Отметить ли сразу как оплаченный

        Returns:
            Обновленный объект Exchange или None в случае ошибки
        """
        if await self.is_user_exchange_banned(counterpart_id):
            logger.warning(f"[Биржа] Пользователь {counterpart_id} забанен на бирже")
            return None

        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if (
                not exchange
                or exchange.status != "active"
                or exchange.counterpart_id is not None
            ):
                return None

            exchange.counterpart_id = counterpart_id
            exchange.status = "sold"
            exchange.sold_at = func.current_timestamp()

            if mark_as_paid:
                exchange.is_paid = True

            await self.session.commit()
            await self.session.refresh(exchange)
            logger.info(
                f"[Биржа] Сделка {exchange_id} принята пользователем {counterpart_id}"
            )
            return exchange
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка принятия сделки {exchange_id}: {e}")
            await self.session.rollback()
            return None

    # Backward compatibility alias
    async def buy_exchange(
        self, exchange_id: int, buyer_id: int, mark_as_paid: bool = False
    ) -> Exchange | None:
        """Deprecated: Use accept_exchange instead."""
        logger.warning("[Биржа] buy_exchange deprecated, use accept_exchange")
        return await self.accept_exchange(exchange_id, buyer_id, mark_as_paid)

    async def mark_exchange_paid(self, exchange_id: int) -> bool:
        """Отметка о наличии оплаты.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            True если успешно отмечен как оплаченный, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)

            exchange.is_paid = True
            await self.session.commit()
            logger.info(f"[Биржа] Сделка {exchange_id} отмечена как оплаченная")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка отметки оплаты сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def update_exchange_date(
        self,
        exchange_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> bool:
        """Обновление даты и времени сделки.

        Args:
            exchange_id: Идентификатор сделки
            start_time: Новое время начала смены
            end_time: Новое время окончания смены

        Returns:
            True если успешно обновлено, False иначе
        """
        if start_time is None and end_time is None:
            logger.warning("[Биржа] Не указаны параметры для обновления даты")
            return False

        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена")
                return False

            if start_time is not None:
                exchange.start_time = start_time
            if end_time is not None:
                exchange.end_time = end_time

            await self.session.commit()
            logger.info(f"[Биржа] Обновлена дата сделки {exchange_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка обновления даты сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def update_exchange_price(self, exchange_id: int, price: int) -> bool:
        """Обновление цены сделки.

        Args:
            exchange_id: Идентификатор сделки
            price: Новая цена

        Returns:
            True если успешно обновлено, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена")
                return False

            exchange.price = price
            await self.session.commit()
            logger.info(f"[Биржа] Обновлена цена сделки {exchange_id} на {price}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка обновления цены сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def update_payment_timing(
        self,
        exchange_id: int,
        payment_type: Optional[str] = None,
        payment_date: Optional[datetime] = None,
    ) -> bool:
        """Обновление условий оплаты сделки.

        Args:
            exchange_id: Идентификатор сделки
            payment_type: Тип оплаты ('immediate' или 'on_date')
            payment_date: Дата оплаты (если payment_type == 'on_date')

        Returns:
            True если успешно обновлено, False иначе
        """
        if payment_type is None and payment_date is None:
            logger.warning("[Биржа] Не указаны параметры для обновления условий оплаты")
            return False

        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена")
                return False

            if payment_type is not None:
                exchange.payment_type = payment_type
            if payment_date is not None:
                exchange.payment_date = payment_date

            await self.session.commit()
            logger.info(f"[Биржа] Обновлены условия оплаты сделки {exchange_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(
                f"[Биржа] Ошибка обновления условий оплаты сделки {exchange_id}: {e}"
            )
            await self.session.rollback()
            return False

    async def update_exchange_comment(
        self, exchange_id: int, comment: Optional[str]
    ) -> bool:
        """Обновление комментария к сделке.

        Args:
            exchange_id: Идентификатор сделки
            comment: Новый комментарий

        Returns:
            True если успешно обновлено, False иначе
        """
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена")
                return False

            exchange.comment = comment
            await self.session.commit()
            logger.info(f"[Биржа] Обновлен комментарий сделки {exchange_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(
                f"[Биржа] Ошибка обновления комментария сделки {exchange_id}: {e}"
            )
            await self.session.rollback()
            return False

    async def update_exchange(
        self,
        exchange_id: int,
        **kwargs,
    ) -> bool:
        """Универсальное обновление полей сделки.

        Args:
            exchange_id: Идентификатор сделки
            **kwargs: Словарь полей для обновления. Поддерживаемые поля:
                     start_time, end_time, price, comment, payment_type, payment_date,
                     is_private

        Returns:
            True если успешно обновлено, False иначе
        """
        if not kwargs:
            logger.warning("[Биржа] Не указаны параметры для обновления")
            return False

        # Разрешенные поля для обновления
        allowed_fields = {
            "start_time",
            "end_time",
            "price",
            "comment",
            "payment_type",
            "payment_date",
            "is_private",
            "is_paid",
            "status",
            "in_owner_schedule",
            "in_counterpart_schedule",
            "counterpart_id",
            "owner_id",
            "owner_intent",
        }

        # Фильтруем только разрешенные поля
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            logger.warning("[Биржа] Нет допустимых полей для обновления")
            return False

        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                logger.warning(f"[Биржа] Сделка с ID {exchange_id} не найдена")
                return False

            # Обновляем поля
            for field, value in update_fields.items():
                setattr(exchange, field, value)

            await self.session.commit()
            logger.info(
                f"[Биржа] Обновлена сделка {exchange_id}, поля: {list(update_fields.keys())}"
            )
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка обновления сделки {exchange_id}: {e}")
            await self.session.rollback()
            return False

    async def get_exchange_by_id(self, exchange_id: int) -> Exchange | None:
        """Получение сделки по ID.

        Args:
            exchange_id: Идентификатор сделки

        Returns:
            Объект Exchange или None
        """
        try:
            query = select(Exchange).where(Exchange.id == exchange_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения сделки {exchange_id}: {e}")
            return None

    async def get_active_exchanges(
        self,
        include_private: bool = False,
        exclude_user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        division: str | list[str] = None,
        owner_intent: Optional[str] = None,
    ) -> Sequence[Exchange]:
        """Получение активных обменов.

        Args:
            include_private: Включать ли приватные сделки
            exclude_user_id: Исключить сделки этого пользователя
            limit: Лимит записей
            offset: Смещение
            division: Направление
            owner_intent: Намерение владельца ('sell' или 'buy')

        Returns:
            Список активных обменов
        """
        try:
            filters = [Exchange.status == "active"]

            if not include_private:
                filters.append(Exchange.is_private.is_(False))

            if owner_intent:
                filters.append(Exchange.owner_intent == owner_intent)

            # Джойним по owner_id чтобы получить информацию о владельце объявления
            query = select(Exchange).join(
                Employee, Employee.user_id == Exchange.owner_id
            )

            if exclude_user_id:
                filters.append(Exchange.owner_id != exclude_user_id)

            if division:
                if isinstance(division, list):
                    filters.append(Employee.division.in_(division))
                else:
                    filters.append(Employee.division == division)

            query = (
                query.where(and_(*filters))
                .order_by(desc(Exchange.created_at))
                .limit(limit)
                .offset(offset)
            )

            result = await self.session.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения активных обменов: {e}")
            return []

    async def get_upcoming_sold_exchanges(
        self,
        start_after: datetime,
        start_before: Optional[datetime] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> Sequence[Exchange]:
        """Получить проданные обмены, которые еще не начались.

        Args:
            start_after: Получить обмены, начинающиеся после этого времени
            start_before: Получить обмены, начинающиеся до этого времени (опционально)
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Список проданных обменов, которые еще не начались
        """
        query = select(Exchange).where(
            Exchange.status == "sold",
            Exchange.start_time.is_not(None),
            Exchange.start_time > start_after,
        )

        if start_before is not None:
            query = query.where(Exchange.start_time <= start_before)

        query = query.order_by(Exchange.start_time).limit(limit).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_users_with_unpaid_exchanges(
        self, status: str = "sold", is_paid: bool = False
    ) -> List[dict]:
        """Get users with their unpaid exchanges grouped.

        Returns:
            List of dicts with format:
            [
                {
                    "user_id": 12345,
                    "exchanges": [Exchange1, Exchange2, ...]
                },
                ...
            ]
        """
        from collections import defaultdict

        # Получаем все неоплаченные проданные обмены
        query = (
            select(Exchange)
            .where(
                and_(
                    Exchange.status == status,
                    Exchange.is_paid == is_paid,
                    Exchange.counterpart_id.isnot(None),  # Только принятые обмены
                )
            )
            .order_by(Exchange.created_at.desc())
        )

        result = await self.session.execute(query)
        exchanges = result.scalars().all()

        if not exchanges:
            return []

        # Группируем обмены по тому, кто должен оплатить
        users_exchanges = defaultdict(list)
        for exchange in exchanges:
            # Определяем, кто должен платить в зависимости от намерения владельца
            if exchange.owner_intent == "sell":
                # Владелец продает смену, платит принимающая сторона
                payer_id = exchange.counterpart_id
            elif exchange.owner_intent == "buy":
                # Владелец хочет купить смену, платит владелец
                payer_id = exchange.owner_id
            else:
                # Fallback на старое поведение для безопасности
                payer_id = exchange.counterpart_id

            if payer_id:
                users_exchanges[payer_id].append(exchange)

        # Формируем результат в нужном формате
        result_list = []
        for user_id, user_exchanges in users_exchanges.items():
            result_list.append({"user_id": user_id, "exchanges": user_exchanges})

        return result_list

    async def get_recent_exchanges(
        self, created_after: datetime, include_private: bool = False, limit: int = 50
    ) -> Sequence[Exchange]:
        """Get exchanges created after specified time.

        Args:
            created_after: Minimum creation time
            include_private: Whether to include private exchanges
            limit: Maximum number of exchanges to return

        Returns:
            List of exchanges created after the specified time
        """
        query = (
            select(Exchange)
            .where(and_(Exchange.created_at >= created_after))
            .order_by(Exchange.created_at.desc())
            .limit(limit)
        )

        # Добавляем фильтр для приватности если нужно
        if not include_private:
            query = query.where(Exchange.is_private is False)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_exchanges_by_payment_date(
        self,
        payment_date: date,
        status: str = "sold",
        is_paid: bool = False,
        limit: int = 100,
    ) -> Sequence[Exchange]:
        """Get exchanges by payment date.

        Args:
            payment_date: Date when payment is due
            status: Exchange status (default "sold")
            is_paid: Payment status (default False)
            limit: Maximum number of exchanges to return

        Returns:
            List of exchanges matching the payment date criteria
        """
        query = (
            select(Exchange)
            .where(
                and_(
                    Exchange.payment_date == payment_date,
                    Exchange.status == status,
                    Exchange.is_paid == is_paid,
                    Exchange.counterpart_id.isnot(None),  # Только принятые обмены
                )
            )
            .order_by(Exchange.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_immediate_unpaid_exchanges(
        self,
        status: str = "sold",
        is_paid: bool = False,
        payment_type: str = "immediate",
        limit: int = 100,
    ) -> Sequence[Exchange]:
        """Get immediate unpaid exchanges.

        Args:
            status: Exchange status (default "sold")
            is_paid: Payment status (default False)
            payment_type: Payment type (default "immediate")
            limit: Maximum number of exchanges to return

        Returns:
            List of immediate unpaid exchanges
        """
        query = (
            select(Exchange)
            .where(
                and_(
                    Exchange.status == status,
                    Exchange.is_paid == is_paid,
                    Exchange.payment_type == payment_type,
                    Exchange.counterpart_id.isnot(None),  # Только принятые обмены
                )
            )
            .order_by(Exchange.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_exchanges(
        self,
        user_id: int,
        exchange_type: str = "all",
        intent: str = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Exchange]:
        """Получение обменов пользователя.

        Args:
            user_id: Идентификатор пользователя
            exchange_type: Тип обменов
            intent: Намерение владельца (sell или buy)
            status: Фильтр по статусу
            limit: Лимит записей
            offset: Смещение

        Returns:
            Список обменов пользователя
        """
        try:
            filters = []

            if exchange_type == "owned":
                filters.append(Exchange.owner_id == user_id)
            elif exchange_type == "counterpart":
                filters.append(Exchange.counterpart_id == user_id)
            else:  # "all"
                filters.append(
                    or_(
                        Exchange.owner_id == user_id, Exchange.counterpart_id == user_id
                    )
                )

            if status:
                filters.append(Exchange.status == status)

            if intent:
                filters.append(Exchange.owner_intent == intent)

            query = (
                select(Exchange)
                .where(and_(*filters))
                .order_by(desc(Exchange.created_at))
                .limit(limit)
                .offset(offset)
            )

            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[Биржа] Ошибка получения обменов пользователя {user_id}: {e}"
            )
            return []

    async def get_exchanges_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> Sequence[Exchange]:
        """Получение обменов за период.

        Args:
            start_date: Начальная дата и время
            end_date: Конечная дата и время
            status: Фильтр по статусу
            limit: Лимит записей

        Returns:
            Список обменов за период
        """
        try:
            filters = [
                Exchange.start_time >= start_date,
                Exchange.start_time <= end_date,
            ]

            if status:
                filters.append(Exchange.status == status)

            query = (
                select(Exchange)
                .where(and_(*filters))
                .order_by(asc(Exchange.start_time))
                .limit(limit)
            )

            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения обменов за период: {e}")
            return []

    async def get_sales_stats_for_period(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """Подсчет продаж за период.

        Args:
            user_id: Идентификатор пользователя
            start_date: Начальная дата и время
            end_date: Конечная дата и время

        Returns:
            Словарь со статистикой продаж
        """
        try:
            query = select(
                func.count(Exchange.id).label("total_sales"),
                func.sum(Exchange.price).label("total_amount"),
                func.avg(Exchange.price).label("average_price"),
            ).where(
                and_(
                    Exchange.owner_id == user_id,
                    Exchange.status == "sold",
                    Exchange.start_time >= start_date,
                    Exchange.start_time <= end_date,
                )
            )

            result = await self.session.execute(query)
            row = result.first()

            return {
                "total_sales": row.total_sales or 0,
                "total_amount": float(row.total_amount or 0),
                "average_price": float(row.average_price or 0),
                "period_start": start_date,
                "period_end": end_date,
            }
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения статистики продаж: {e}")
            return {
                "total_sales": 0,
                "total_amount": 0.0,
                "average_price": 0.0,
                "period_start": start_date,
                "period_end": end_date,
            }

    async def get_purchases_stats_for_period(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """Подсчет покупок за период.

        Args:
            user_id: Идентификатор пользователя
            start_date: Начальная дата и время
            end_date: Конечная дата и время

        Returns:
            Словарь со статистикой покупок
        """
        try:
            query = select(
                func.count(Exchange.id).label("total_purchases"),
                func.sum(Exchange.price).label("total_amount"),
                func.avg(Exchange.price).label("average_price"),
            ).where(
                and_(
                    Exchange.counterpart_id == user_id,
                    Exchange.status == "sold",
                    Exchange.start_time >= start_date,
                    Exchange.start_time <= end_date,
                )
            )

            result = await self.session.execute(query)
            row = result.first()

            return {
                "total_purchases": row.total_purchases or 0,
                "total_amount": float(row.total_amount or 0),
                "average_price": float(row.average_price or 0),
                "period_start": start_date,
                "period_end": end_date,
            }
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения статистики покупок: {e}")
            return {
                "total_purchases": 0,
                "total_amount": 0.0,
                "average_price": 0.0,
                "period_start": start_date,
                "period_end": end_date,
            }

    async def create_subscription(
        self,
        subscriber_id: int,
        name: Optional[str] = None,
        exchange_type: str = "buy",
        subscription_type: str = "all",
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        days_of_week: Optional[list] = None,
        target_seller_id: Optional[int] = None,
        target_divisions: Optional[list] = None,
        notify_immediately: bool = True,
        notify_daily_digest: bool = False,
        notify_before_expire: bool = False,
        digest_time: time = time(9, 0),
    ) -> ExchangeSubscription | None:
        """Создание новой подписки на обмены.

        Args:
            subscriber_id: Идентификатор подписчика
            name: Название подписки
            exchange_type: Тип обменов ('buy', 'sell', 'both')
            subscription_type: Тип подписки ('all', 'price_range', 'date_range', 'time_range', 'seller_specific')
            min_price: Минимальная цена
            max_price: Максимальная цена
            start_date: Начальная дата диапазона
            end_date: Конечная дата диапазона
            start_time: Начальное время дня
            end_time: Конечное время дня
            days_of_week: Дни недели [1,2,3,4,5]
            target_seller_id: Конкретный продавец
            target_divisions: Подразделения
            notify_immediately: Уведомлять сразу
            notify_daily_digest: Ежедневная сводка
            notify_before_expire: Уведомлять перед истечением
            digest_time: Время отправки сводки

        Returns:
            Созданный объект ExchangeSubscription или None
        """
        try:
            subscription = ExchangeSubscription(
                subscriber_id=subscriber_id,
                name=name,
                exchange_type=exchange_type,
                subscription_type=subscription_type,
                min_price=min_price,
                max_price=max_price,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                days_of_week=days_of_week,
                target_seller_id=target_seller_id,
                target_divisions=target_divisions,
                notify_immediately=notify_immediately,
                notify_daily_digest=notify_daily_digest,
                notify_before_expire=notify_before_expire,
                digest_time=digest_time,
            )

            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)

            logger.info(
                f"[Биржа] Создана подписка {subscription.id} '{name}' для пользователя {subscriber_id}"
            )
            return subscription
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка создания подписки: {e}")
            await self.session.rollback()
            return None

    async def deactivate_subscription(
        self,
        subscriber_id: int,
        subscription_id: Optional[int] = None,
    ) -> bool:
        """Деактивация подписки.

        Args:
            subscriber_id: Идентификатор подписчика
            subscription_id: Идентификатор конкретной подписки (опционально)

        Returns:
            True если успешно деактивирована, False иначе
        """
        try:
            if subscription_id:
                # Деактивация конкретной подписки
                query = select(ExchangeSubscription).where(
                    and_(
                        ExchangeSubscription.id == subscription_id,
                        ExchangeSubscription.subscriber_id == subscriber_id,
                    )
                )
                result = await self.session.execute(query)
                subscription = result.scalar_one_or_none()

                if subscription:
                    subscription.is_active = False
                    await self.session.commit()
                    logger.info(f"[Биржа] Деактивирована подписка {subscription_id}")
                    return True
            else:
                # Деактивация всех подписок пользователя
                query = select(ExchangeSubscription).where(
                    and_(
                        ExchangeSubscription.subscriber_id == subscriber_id,
                        ExchangeSubscription.is_active,
                    )
                )
                result = await self.session.execute(query)
                subscriptions = result.scalars().all()

                for subscription in subscriptions:
                    subscription.is_active = False

                await self.session.commit()
                logger.info(
                    f"[Биржа] Деактивированы все подписки пользователя {subscriber_id}"
                )
                return True

            return False
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка деактивации подписки: {e}")
            await self.session.rollback()
            return False

    async def get_user_subscriptions(
        self,
        subscriber_id: int,
        active_only: bool = True,
    ) -> Sequence[ExchangeSubscription]:
        """Получение подписок пользователя.

        Args:
            subscriber_id: Идентификатор подписчика
            active_only: Только активные подписки

        Returns:
            Список подписок пользователя
        """
        try:
            filters = [ExchangeSubscription.subscriber_id == subscriber_id]

            if active_only:
                filters.append(ExchangeSubscription.is_active)

            query = (
                select(ExchangeSubscription)
                .where(and_(*filters))
                .order_by(desc(ExchangeSubscription.created_at))
            )

            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"[Биржа] Ошибка получения подписок пользователя {subscriber_id}: {e}"
            )
            return []

    async def ban_user_from_exchange(self, user_id: int) -> bool:
        """Бан пользователя на бирже.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            True если успешно забанен, False иначе
        """
        try:
            query = select(Employee).where(Employee.user_id == user_id)
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()

            if employee:
                employee.is_exchange_banned = True
                await self.session.commit()
                logger.info(f"[Биржа] Пользователь {user_id} забанен на бирже")
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка бана пользователя {user_id}: {e}")
            await self.session.rollback()
            return False

    async def unban_user_from_exchange(self, user_id: int) -> bool:
        """Разбан пользователя на бирже.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            True если успешно разбанен, False иначе
        """
        try:
            query = select(Employee).where(Employee.user_id == user_id)
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()

            if employee:
                employee.is_exchange_banned = False
                await self.session.commit()
                logger.info(f"[Биржа] Пользователь {user_id} разбанен на бирже")
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка разбана пользователя {user_id}: {e}")
            await self.session.rollback()
            return False

    async def is_user_exchange_banned(self, user_id: int) -> bool:
        """Проверка бана пользователя на бирже.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            True если пользователь забанен, False иначе
        """
        try:
            query = select(Employee.is_exchange_banned).where(
                Employee.user_id == user_id
            )
            result = await self.session.execute(query)
            is_banned = result.scalar_one_or_none()
            return bool(is_banned)
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка проверки бана пользователя {user_id}: {e}")
            return False

    async def update_subscription(
        self,
        subscription_id: int,
        **kwargs,
    ) -> bool:
        """Универсальное обновление подписки.

        Args:
            subscription_id: Идентификатор подписки
            **kwargs: Поля для обновления

        Returns:
            True если успешно обновлено, False иначе
        """
        if not kwargs:
            return False

        # Разрешенные поля для обновления
        allowed_fields = {
            "name",
            "exchange_type",
            "subscription_type",
            "min_price",
            "max_price",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "days_of_week",
            "target_seller_id",
            "target_divisions",
            "notify_immediately",
            "notify_daily_digest",
            "notify_before_expire",
            "digest_time",
            "is_active",
        }

        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not update_fields:
            return False

        try:
            query = select(ExchangeSubscription).where(
                ExchangeSubscription.id == subscription_id
            )
            result = await self.session.execute(query)
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.warning(f"[Биржа] Подписка {subscription_id} не найдена")
                return False

            for field, value in update_fields.items():
                setattr(subscription, field, value)

            await self.session.commit()
            logger.info(f"[Биржа] Обновлена подписка {subscription_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка обновления подписки {subscription_id}: {e}")
            await self.session.rollback()
            return False

    async def delete_subscription(
        self,
        subscription_id: int,
    ) -> bool:
        """Удаление подписки по ID.

        Args:
            subscription_id: Идентификатор подписки

        Returns:
            True если успешно удалена, False иначе
        """
        try:
            query = select(ExchangeSubscription).where(
                ExchangeSubscription.id == subscription_id
            )
            result = await self.session.execute(query)
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.warning(f"[Биржа] Подписка {subscription_id} не найдена")
                return False

            await self.session.delete(subscription)
            await self.session.commit()
            logger.info(f"[Биржа] Удалена подписка {subscription_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка удаления подписки {subscription_id}: {e}")
            await self.session.rollback()
            return False

    async def get_subscription_by_id(
        self,
        subscription_id: int,
        subscriber_id: Optional[int] = None,
    ) -> ExchangeSubscription | None:
        """Получение подписки по ID.

        Args:
            subscription_id: Идентификатор подписки
            subscriber_id: Идентификатор подписчика (для фильтрации)

        Returns:
            Объект ExchangeSubscription или None
        """
        try:
            filters = [ExchangeSubscription.id == subscription_id]
            if subscriber_id:
                filters.append(ExchangeSubscription.subscriber_id == subscriber_id)

            query = select(ExchangeSubscription).where(and_(*filters))
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения подписки {subscription_id}: {e}")
            return None

    async def find_matching_subscriptions(
        self,
        exchange: Exchange,
    ) -> Sequence[ExchangeSubscription]:
        """Поиск подписок, которые соответствуют новому обмену.

        Args:
            exchange: Объект Exchange для проверки

        Returns:
            Список подходящих подписок
        """
        try:
            base_filters = [
                ExchangeSubscription.is_active.is_(True),
                ExchangeSubscription.notify_immediately.is_(True),
            ]

            # Фильтр по типу обмена
            exchange_type_filters = or_(
                ExchangeSubscription.exchange_type == "both",
                ExchangeSubscription.exchange_type == exchange.owner_intent,
            )
            base_filters.append(exchange_type_filters)

            # Фильтр по цене
            price_filters = []
            if exchange.price is not None:
                price_filters.extend([
                    or_(
                        ExchangeSubscription.min_price.is_(None),
                        ExchangeSubscription.min_price <= exchange.price,
                    ),
                    or_(
                        ExchangeSubscription.max_price.is_(None),
                        ExchangeSubscription.max_price >= exchange.price,
                    ),
                ])

            # Фильтр по продавцу и исключение собственных обменов
            # Определяем пользователя, создавшего обмен
            creator_id = exchange.owner_id

            if exchange.owner_intent == "sell":
                # Владелец продает смену - он и есть продавец
                seller_filter = or_(
                    ExchangeSubscription.target_seller_id.is_(None),
                    ExchangeSubscription.target_seller_id == exchange.owner_id,
                )
            elif exchange.owner_intent == "buy":
                # Владелец хочет купить смену - target_seller_id не применим
                seller_filter = ExchangeSubscription.target_seller_id.is_(None)
            else:
                # Fallback для неизвестного типа
                seller_filter = or_(
                    ExchangeSubscription.target_seller_id.is_(None),
                    ExchangeSubscription.target_seller_id == exchange.owner_id,
                )

            base_filters.append(seller_filter)

            # Исключаем собственные обмены создателя
            if creator_id:
                base_filters.append(ExchangeSubscription.subscriber_id != creator_id)

            all_filters = base_filters + price_filters

            query = (
                select(ExchangeSubscription)
                .join(Employee, Employee.user_id == ExchangeSubscription.subscriber_id)
                .where(and_(*all_filters))
            )

            result = await self.session.execute(query)
            subscriptions = result.scalars().all()

            # Дополнительная фильтрация в Python для сложных условий
            matching_subscriptions = []
            for sub in subscriptions:
                if self._subscription_matches_exchange(sub, exchange):
                    matching_subscriptions.append(sub)

            return matching_subscriptions
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка поиска подходящих подписок: {e}")
            return []

    def _subscription_matches_exchange(
        self,
        subscription: ExchangeSubscription,
        exchange: Exchange,
    ) -> bool:
        """Проверка соответствия подписки обмену."""
        # Проверка даты
        if exchange.start_time:
            exchange_date = exchange.start_time.date()
            if subscription.start_date and exchange_date < subscription.start_date:
                return False
            if subscription.end_date and exchange_date > subscription.end_date:
                return False

            # Проверка времени
            exchange_time = exchange.start_time.time()
            if subscription.start_time and exchange_time < subscription.start_time:
                return False
            if subscription.end_time and exchange_time > subscription.end_time:
                return False

            # Проверка дней недели (1=Monday, 7=Sunday)
            if subscription.days_of_week:
                weekday = (
                    exchange.start_time.weekday() + 1
                )  # Python: 0=Monday, SQL: 1=Monday
                if weekday not in subscription.days_of_week:
                    return False

        # Проверка подразделений
        if subscription.target_divisions and exchange.owner and exchange.owner.division:
            if exchange.owner.division not in subscription.target_divisions:
                return False

        return True

    async def record_notification(
        self,
        subscription_id: int,
        exchange_id: int,
        notification_type: str = "immediate",
    ) -> SubscriptionNotification | None:
        """Запись уведомления в историю.

        Args:
            subscription_id: Идентификатор подписки
            exchange_id: Идентификатор обмена
            notification_type: Тип уведомления ('immediate', 'digest', 'expiry')

        Returns:
            Созданный объект SubscriptionNotification или None
        """
        try:
            notification = SubscriptionNotification(
                subscription_id=subscription_id,
                exchange_id=exchange_id,
                notification_type=notification_type,
            )

            self.session.add(notification)

            # Обновляем статистику подписки
            subscription = await self.get_subscription_by_id(subscription_id)
            if subscription:
                subscription.notifications_sent += 1
                subscription.last_notified_at = func.current_timestamp()

            await self.session.commit()
            await self.session.refresh(notification)

            logger.info(
                f"[Биржа] Записано уведомление: подписка {subscription_id}, обмен {exchange_id}"
            )
            return notification
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка записи уведомления: {e}")
            await self.session.rollback()
            return None

    async def get_subscriptions_for_digest(
        self,
        digest_time: time,
    ) -> Sequence[ExchangeSubscription]:
        """Получение подписок для отправки дневной сводки.

        Args:
            digest_time: Время отправки сводки

        Returns:
            Список подписок для сводки
        """
        try:
            query = select(ExchangeSubscription).where(
                and_(
                    ExchangeSubscription.is_active.is_(True),
                    ExchangeSubscription.notify_daily_digest.is_(True),
                    ExchangeSubscription.digest_time == digest_time,
                )
            )

            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка получения подписок для сводки: {e}")
            return []

    async def update_digest_timestamp(
        self,
        subscription_id: int,
    ) -> bool:
        """Обновление времени последней сводки.

        Args:
            subscription_id: Идентификатор подписки

        Returns:
            True если успешно обновлено
        """
        try:
            subscription = await self.get_subscription_by_id(subscription_id)
            if subscription:
                subscription.last_digest_at = func.current_timestamp()
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка обновления времени сводки: {e}")
            await self.session.rollback()
            return False
