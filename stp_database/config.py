"""Конфигурация для подключения к БД."""

from dataclasses import dataclass
from typing import Optional

import pytz
from pytz.tzinfo import DstTzInfo
from sqlalchemy import URL


@dataclass
class DbConfig:
    """Конфигурация подключения к базе данных.

    Attributes:
        host: Хост, на котором находится база данных
        user: Логин для авторизации в базе данных
        password: Пароль для авторизации в базе данных
        port: Порт для подключения к базе данных (по умолчанию 3306)
    """

    host: str
    user: str
    password: str
    port: int = 3306
    tz: DstTzInfo = pytz.timezone("Asia/Yekaterinburg")

    def construct_sqlalchemy_url(
        self,
        db_name: Optional[str] = None,
        driver: str = "aiomysql",
    ) -> URL:
        """Создание SQLAlchemy URL для подключения к базе данных MariaDB.

        Args:
            db_name: Название базы данных для подключения (опционально)
            driver: MySQL драйвер для использования (по умолчанию "aiomysql")

        Returns:
            Объект SQLAlchemy URL для подключения к базе данных
        """
        connection_url = URL.create(
            f"mysql+{driver}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=db_name,
            query={
                "charset": "utf8mb4",
                "use_unicode": "1",
                "sql_mode": "TRADITIONAL",
                "connect_timeout": "30",
                "autocommit": "false",
            },
        )

        return connection_url
