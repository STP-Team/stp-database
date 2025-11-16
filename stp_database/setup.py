"""Создание движков и сессий."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from stp_database.config import DbConfig


def create_engine(db: DbConfig, db_name: str, echo: bool = False) -> AsyncEngine:
    """Создает асинхронный движок SQLAlchemy для подключения к базе данных.

    Args:
        db (DbConfig): Конфигурация базы данных.
        db_name (str): Имя базы данных для подключения.
        echo (bool, optional): Включить логирование SQL-запросов. По умолчанию False.

    Returns:
        AsyncEngine: Асинхронный движок SQLAlchemy с настроенным пулом соединений.
    """
    engine = create_async_engine(
        db.construct_sqlalchemy_url(db_name),
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True,
        echo=echo,
        connect_args={
            "autocommit": False,
            "charset": "utf8mb4",
            "use_unicode": True,
            "sql_mode": "TRADITIONAL",
            "connect_timeout": 30,
        },
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_timeout=30,
        pool_reset_on_return="commit",
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
