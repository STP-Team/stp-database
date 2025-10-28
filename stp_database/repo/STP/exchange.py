"""Репозиторий функций для взаимодействия с биржей смен."""

import logging
from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.exc import SQLAlchemyError

from stp_database.models.STP.employee import Employee
from stp_database.models.STP.exchange import Exchange, ExchangeSubscription
from stp_database.repo.base import BaseRepo

logger = logging.getLogger(__name__)


class ExchangeRepo(BaseRepo):
    """Репозиторий для работы с биржей смен."""

    async def create_exchange(
        self,
        seller_id: int,
        start_time: Optional[datetime],
        price: int,
        exchange_type: str = "sell",
        end_time: Optional[datetime] = None,
        comment: Optional[str] = None,
        is_private: bool = False,
        payment_type: str = "immediate",
        payment_date: Optional[datetime] = None,
    ) -> Exchange | None:
        """Создание нового сделки смены.

        Args:
            seller_id: Идентификатор продавца
            start_time: Начало смены
            price: Цена за смену
            exchange_type: Тип обмена ('sell' или 'buy')
            end_time: Окончание смены (если частичная смена)
            comment: Комментарий к сделке
            is_private: Приватный ли сделка
            payment_type: Тип оплаты ('immediate' или 'on_date')
            payment_date: Дата оплаты (если payment_type == 'on_date')

        Returns:
            Созданный объект Exchange или None в случае ошибки
        """
        # Проверяем, что пользователь не забанен
        if await self.is_user_exchange_banned(seller_id):
            logger.warning(f"[Биржа] Пользователь {seller_id} забанен на бирже")
            return None

        new_exchange = Exchange(
            seller_id=seller_id,
            start_time=start_time,
            end_time=end_time,
            price=price,
            type=exchange_type,
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
                f"[Биржа] Создан новый сделка: {new_exchange.id} от пользователя {seller_id}"
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

    async def buy_exchange(
        self, exchange_id: int, buyer_id: int, mark_as_paid: bool = False
    ) -> Exchange | None:
        """Покупка сделки.

        Args:
            exchange_id: Идентификатор сделки
            buyer_id: Идентификатор покупателя
            mark_as_paid: Отметить ли сразу как оплаченный

        Returns:
            Обновленный объект Exchange или None в случае ошибки
        """
        if await self.is_user_exchange_banned(buyer_id):
            logger.warning(f"[Биржа] Покупатель {buyer_id} забанен на бирже")
            return None

        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if (
                not exchange
                or exchange.status != "active"
                or exchange.buyer_id is not None
            ):
                return None

            exchange.buyer_id = buyer_id
            exchange.status = "sold"
            exchange.sold_at = func.current_timestamp()

            if mark_as_paid:
                exchange.is_paid = True

            await self.session.commit()
            await self.session.refresh(exchange)
            logger.info(
                f"[Биржа] Сделка {exchange_id} куплена пользователем {buyer_id}"
            )
            return exchange
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка покупки сделки {exchange_id}: {e}")
            await self.session.rollback()
            return None

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
            "in_schedule",
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
        exchange_type: Optional[str] = None,
    ) -> Sequence[Exchange]:
        """Получение активных обменов.

        Args:
            include_private: Включать ли приватные сделки
            exclude_user_id: Исключить сделки этого пользователя
            limit: Лимит записей
            offset: Смещение
            division: Направление
            exchange_type: Тип обмена ('sell' или 'buy')

        Returns:
            Список активных обменов
        """
        try:
            filters = [Exchange.status == "active"]

            if not include_private:
                filters.append(Exchange.is_private.is_(False))

            if exclude_user_id:
                filters.append(Exchange.seller_id != exclude_user_id)

            if exchange_type:
                filters.append(Exchange.type == exchange_type)

            query = select(Exchange).join(
                Employee, Employee.user_id == Exchange.seller_id
            )

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

    async def get_user_exchanges(
        self,
        user_id: int,
        exchange_type: str = "all",  # "sold", "bought", "all"
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Exchange]:
        """Получение обменов пользователя.

        Args:
            user_id: Идентификатор пользователя
            exchange_type: Тип обменов ("sold", "bought", "all")
            status: Фильтр по статусу
            limit: Лимит записей
            offset: Смещение

        Returns:
            Список обменов пользователя
        """
        try:
            filters = []

            if exchange_type == "sold":
                filters.append(Exchange.seller_id == user_id)
            elif exchange_type == "bought":
                filters.append(Exchange.buyer_id == user_id)
            else:  # "all"
                filters.append(
                    or_(Exchange.seller_id == user_id, Exchange.buyer_id == user_id)
                )

            if status:
                filters.append(Exchange.status == status)

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
                    Exchange.seller_id == user_id,
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
                    Exchange.buyer_id == user_id,
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

    async def subscribe_to_exchanges(
        self,
        subscriber_id: int,
        subscription_type: str = "all",
        exchange_id: Optional[int] = None,
    ) -> ExchangeSubscription | None:
        """Подписка на новые подмены.

        Args:
            subscriber_id: Идентификатор подписчика
            subscription_type: Тип подписки ('all', 'specific_exchange', 'specific_seller')
            exchange_id: Идентификатор сделки (для подписки на конкретный сделка)

        Returns:
            Созданный объект ExchangeSubscription или None
        """
        try:
            # Проверяем, нет ли уже такой подписки
            existing_query = select(ExchangeSubscription).where(
                and_(
                    ExchangeSubscription.subscriber_id == subscriber_id,
                    ExchangeSubscription.subscription_type == subscription_type,
                    ExchangeSubscription.is_active,
                )
            )

            if exchange_id:
                existing_query = existing_query.where(
                    ExchangeSubscription.exchange_id == exchange_id
                )

            result = await self.session.execute(existing_query)
            if result.scalar_one_or_none():
                logger.info(
                    f"[Биржа] Подписка уже существует для пользователя {subscriber_id}"
                )
                return None

            subscription = ExchangeSubscription(
                subscriber_id=subscriber_id,
                subscription_type=subscription_type,
                exchange_id=exchange_id,
            )

            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)

            logger.info(
                f"[Биржа] Создана подписка {subscription.id} для пользователя {subscriber_id}"
            )
            return subscription
        except SQLAlchemyError as e:
            logger.error(f"[Биржа] Ошибка создания подписки: {e}")
            await self.session.rollback()
            return None

    async def unsubscribe_from_exchanges(
        self,
        subscriber_id: int,
        subscription_id: Optional[int] = None,
    ) -> bool:
        """Отписка от уведомлений.

        Args:
            subscriber_id: Идентификатор подписчика
            subscription_id: Идентификатор конкретной подписки (опционально)

        Returns:
            True если успешно отписан, False иначе
        """
        try:
            if subscription_id:
                # Отписка от конкретной подписки
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
                # Отписка от всех подписок пользователя
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
            logger.error(f"[Биржа] Ошибка отписки: {e}")
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
