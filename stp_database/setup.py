"""Создание движков и сессий."""

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(
    db_name: str,
    host: str = "localhost",
    port: int = 3306,
    username: str = "root",
    password: str = "",
    driver: str = "aiomysql",
    echo: bool = False,
) -> AsyncEngine:
    """Создает асинхронный движок SQLAlchemy для подключения к базе данных.

    Args:
        db_name (str): Имя базы данных для подключения.
        host (str, optional): Хост базы данных. По умолчанию "localhost".
        port (int, optional): Порт базы данных. По умолчанию 3306.
        username (str, optional): Имя пользователя. По умолчанию "root".
        password (str, optional): Пароль пользователя. По умолчанию "".
        driver (str, optional): Драйвер для подключения. По умолчанию "aiomysql".
        echo (bool, optional): Включить логирование SQL-запросов. По умолчанию False.

    Returns:
        AsyncEngine: Асинхронный движок SQLAlchemy с настроенным пулом соединений.
    """
    # Конструируем URL для подключения с правильным кодированием спецсимволов
    sqlalchemy_url = URL.create(
        f"mysql+{driver}",
        username=username,
        password=password,
        host=host,
        port=port,
        database=db_name,
    )

    engine = create_async_engine(
        sqlalchemy_url,
        echo=echo,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=15,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={
            "charset": "utf8mb4",
            "connect_timeout": 10,
            "autocommit": False,
        },
    )
    return engine


def create_session_pool(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Создает пул асинхронных сессий SQLAlchemy.

    Args:
        engine (AsyncEngine): Асинхронный движок SQLAlchemy.

    Returns:
        Фабрика для создания асинхронных сессий базы данных.
    """
    session_pool = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return session_pool
