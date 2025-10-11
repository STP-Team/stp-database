# Репозиторий базы данных

Общие модели баз данных и репозитории для ботов СТП. Пакет предоставляет унифицированный уровень базы
данных, который можно устанавливать и использовать в разных проектах ботов.

## Особенности

- Асинхронные модели SQLAlchemy
- Шаблон репозитория для чистого доступа к данным
- Предварительно настроенный движок базы данных и настройка пула сеансов
- Типобезопасные операции с базой данных

## Установка

### Используя UV (Рекомендовано)

Установка напрямую из репозитория:

```bash
uv add git+https://github.com/ERTG-BOTS/stp-database.git
```

Или добавить в `pyproject.toml`:

```toml
[project]
dependencies = [
    "stp-database @ git+https://github.com/ERTG-BOTS/stp-database.git",
]
```

### Используя pip

```bash
pip install git+https://github.com/ERTG-BOTS/stp-database.git
```

## Использование

### Базовая настройка

```python
from stp_database import (
    DbConfig,
    create_engine,
    create_session_pool,
    MainRequestsRepo,
    KPIRequestsRepo,
)

# Создание конфигурации
db_config = DbConfig(
    host="localhost",
    user="your_user",
    password="your_password",
    port=3306
)

# Создание движков
stp_engine = create_engine(db_config, db_name="stp_database", echo=False)
kpi_engine = create_engine(db_config, db_name="kpi_database", echo=False)

# Создание сессий
stp_session_pool = create_session_pool(stp_engine)
kpi_session_pool = create_session_pool(kpi_engine)
```

### Использование с ботами на Aiogram

Вот как интегрировать модуль с ботом, написанным на Aiogram:

```python
from aiogram import Bot, Dispatcher
from stp_database import (
    DbConfig,
    create_engine,
    create_session_pool,
    MainRequestsRepo,
    KPIRequestsRepo,
)


async def main():
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher()

    # Настройка БД
    db_config = DbConfig(
        host="localhost",
        user="bot_user",
        password="bot_password"
    )

    stp_engine = create_engine(db_config, db_name="stp_db")
    kpi_engine = create_engine(db_config, db_name="kpi_db")

    stp_pool = create_session_pool(stp_engine)
    kpi_pool = create_session_pool(kpi_engine)

    # Храним сессии в диспетчере
    dp["stp_pool"] = stp_pool
    dp["kpi_pool"] = kpi_pool

    # Запускаем опрос
    await dp.start_polling(bot)
```

### Использование в Middleware

```python
from aiogram import BaseMiddleware
from stp_database import MainRequestsRepo, KPIRequestsRepo


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, stp_session_pool, kpi_session_pool):
        self.stp_session_pool = stp_session_pool
        self.kpi_session_pool = kpi_session_pool

    async def __call__(self, handler, event, data):
        async with self.stp_session_pool() as stp_session:
            async with self.kpi_session_pool() as kpi_session:
                data["stp_repo"] = MainRequestsRepo(stp_session)
                data["kpi_repo"] = KPIRequestsRepo(kpi_session)

                return await handler(event, data)
```

### Использование репозиториев в Handlers

```python
from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def my_handler(message: Message, stp_repo: MainRequestsRepo):
    # Доступ к сотрудникам
    user = await stp_repo.employee.get_user(user_id=message.from_user.id)

    # Доступ к предметам
    products = await stp_repo.product.get_all_active_products()

    # Доступ к транзакциям
    balance = await stp_repo.transaction.get_balance(user_id=message.from_user.id)

    await message.answer(f"Твой баланс: {balance}")
```

### Доступные репозитории

#### STP (MainRequestsRepo)

- `employee` - Операции с сотрудниками
- `product` - Менеджмент предметов
- `purchase` - Трекинг покупок предметов
- `transaction` - Операции транзакций
- `achievement` - Менеджмент достижений
- `broadcast` - Логи рассылок
- `group` - Менеджмент групп
- `group_member` - Менеджмент участников групп
- `upload` - Логи загруженных файлов

#### KPI (KPIRequestsRepo)

- `spec_day_kpi` - Дневной KPI для специалистов
- `spec_week_kpi` - Недельный KPI для специалистов
- `spec_month_kpi` - Месячный KPI для специалистов
- `spec_premium` - Показатели премии для специалистов
- `head_premium` - Показатели премии для руководителей

### Прямой доступ к моделям

```python
from stp_database.models import Employee, Product
from stp_database.models.STP.transaction import Transaction
from sqlalchemy import select

async with stp_session_pool() as session:
    # Запрос используя модели напрямую
    result = await session.execute(
        select(Employee).where(Employee.telegram_id == 123456)
    )
    user = result.scalar_one_or_none()
```

## Конфигурация используя переменные окружения

Ты можешь загрузить конфигурацию для базы используя env:

```python
import os
from stp_database import DbConfig

db_config = DbConfig(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", "3306"))
)
```

## Разработка

### Структура проекта

```
stp_database/
├── __init__.py          # Основные экспорты
├── config.py            # Класс DbConfig для конфигурации
├── setup.py             # Фабрика движков и сессий 
├── models/              # Модели SQLAlchemy
│   ├── base.py         # Базовые классы моделей
│   ├── STP/            # Модели STP
│   └── KPI/            # Модели KPI
└── repo/               # Репозитории взаимодействия с БД
    ├── base.py         # Базовые классы репозиториев
    ├── STP/            # Репозитории STP
    │   └── requests.py # Агрегатор MainRequestsRepo
    └── KPI/            # Репозитории KPI
        └── requests.py # Агрегатор KPIRequestsRepo
```

### Обновление модуля

Когда ты вносишь изменения в этот модуль:

1. Зафиксируй и отправь изменения в репозиторий GitHub.
2. В своих проектах ботов обнови пакет:

```bash
# Используя uv
uv add --upgrade git+https://github.com/ERTG-BOTS/stp-database.git

# Используя pip
pip install --upgrade git+https://github.com/ERTG-BOTS/stp-database.git
```

### Менеджмент версий

Обнови версию в обоих файлах при выпуске:

- `pyproject.toml` - `version = "x.y.z"`
- `stp_database/__init__.py` - `__version__ = "x.y.z"`

## Миграция ботов

Если в проекте используется структура - `infrastructure.database`:

### До:

```python
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.repo.STP.requests import MainRequestsRepo
from infrastructure.database.models import Employee
```

### После:

```python
from stp_database import create_engine, create_session_pool, MainRequestsRepo
from stp_database.models import Employee
```

Весь функционал остается тем же, меняются только пути импортов.

## Требования

- Python >= 3.13
- SQLAlchemy >= 2.0.43
- aiomysql >= 0.2.0

## Лицензия

Private - Только для внутреннего использования
