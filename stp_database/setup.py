"""Создание движков и сессий."""

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
    # Конструируем URL для подключения
    sqlalchemy_url = f"mysql+{driver}://{username}:{password}@{host}:{port}/{db_name}"

    engine = create_async_engine(
        sqlalchemy_url,
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
