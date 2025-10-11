"""Модели, связанные с сущностями предметов."""

from sqlalchemy import JSON, Integer
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from stp_database.models.base import Base


class Product(Base):
    """Класс, представляющий сущность предмета в БД.

    Args:
        id: Уникальный идентификатор предмета
        name: Название предмета
        description: Описание предмета
        cost: Стоимость предмета в магазине
        count: Кол-во использований предмета
        manager_role: Роль для подтверждения активации предмета

    Methods:
        __repr__(): Возвращает строковое представление объекта Product.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    division: Mapped[str] = mapped_column(VARCHAR(3), nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    activate_days: Mapped[list] = mapped_column(JSON, nullable=True)
    manager_role: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        """Возвращает строковое представление объекта Product."""
        return f"<Product {self.id} {self.name} {self.description} {self.division} {self.cost} {self.count} {self.manager_role}>"
