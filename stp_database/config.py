from dataclasses import dataclass
from typing import Optional

from sqlalchemy import URL


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        Хост, на котором находится база данных
    password : str
        Пароль для авторизации в базе данных.
    user : str
        Логин для авторизации в базе данных.
    port : int
        Порт для подключения к базе данных (по умолчанию 3306)
    """

    host: str
    user: str
    password: str
    port: int = 3306

    def construct_sqlalchemy_url(
        self,
        db_name: Optional[str] = None,
        driver: str = "aiomysql",
    ) -> URL:
        """
        Constructs and returns SQLAlchemy URL for MariaDB database connection

        Parameters
        ----------
        db_name : str, optional
            Name of the database to connect to
        driver : str, default="aiomysql"
            The MySQL driver to use (aiomysql, pymysql, etc.)

        Returns
        -------
        URL
            SQLAlchemy URL object for database connection
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
