# Setup Guide for STP Database Package

This guide will walk you through publishing the database package to a private GitHub repository and installing it in your bots.

## Step 1: Create a Private GitHub Repository

1. Go to GitHub and create a new **private** repository
2. Name it: `stp-database`
3. Don't initialize with README (we already have one)

## Step 2: Initialize Git and Push to GitHub

From the `infrastructure/database` directory:

```bash
cd "/home/roman/Проекты/Дом.ру/stpsher/infrastructure/database"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: STP Database Package v0.1.0"

# Add remote (replace with your actual repository URL)
git remote add origin git@github.com:ERTG-BOTS/stp-database.git

# Push to GitHub
git push -u origin master
```

## Step 3: Install in Your Bots

### Using UV (Recommended)

In your bot project directory:

```bash
# Install from GitHub
uv add git+https://github.com/ERTG-BOTS/stp-database.git

# Or with SSH
uv add git+ssh://git@github.com/your-org/stp-database.git
```

### Using pip

```bash
pip install git+https://github.com/ERTG-BOTS/stp-database.git
```

## Step 4: Update Your Bot Code

### 1. Update imports in your bot

**Old code:**
```python
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.repo.STP.requests import MainRequestsRepo
from infrastructure.database.repo.KPI.requests import KPIRequestsRepo
from infrastructure.database.models import Employee
```

**New code:**
```python
from stp_database import (
    DbConfig,
    create_engine,
    create_session_pool,
    MainRequestsRepo,
    KPIRequestsRepo,
)
from stp_database.models import Employee
```

### 2. Update bot.py

Replace the old database setup:

```python
# OLD
from infrastructure.database.setup import create_engine, create_session_pool

# NEW
from stp_database import DbConfig, create_engine, create_session_pool

# Create DbConfig from your existing config
db_config = DbConfig(
    host=bot_config.db.host,
    user=bot_config.db.user,
    password=bot_config.db.password,
    port=3306
)

# Rest remains the same
main_db_engine = create_engine(db_config, db_name=bot_config.db.main_db)
kpi_db_engine = create_engine(db_config, db_name=bot_config.db.kpi_db)
```

### 3. Update middleware

Your middleware should work as-is, just update the imports:

```python
# OLD
from infrastructure.database.repo.KPI.requests import KPIRequestsRepo
from infrastructure.database.repo.STP.requests import MainRequestsRepo

# NEW
from stp_database import MainRequestsRepo, KPIRequestsRepo
```

## Step 5: Test the Installation

Create a simple test file to verify everything works:

```python
# test_db.py
import asyncio
from stp_database import DbConfig, create_engine, create_session_pool, MainRequestsRepo

async def test():
    db_config = DbConfig(
        host="localhost",
        user="test",
        password="test",
        port=3306
    )

    engine = create_engine(db_config, db_name="test_db")
    pool = create_session_pool(engine)

    async with pool() as session:
        repo = MainRequestsRepo(session)
        print("Database connection successful!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python test_db.py
```

## Step 6: Updating the Package

When you need to update the database models or repositories:

### 1. Make changes in the stp-database repository

```bash
cd stp-database
# Make your changes
git add .
git commit -m "Update: description of changes"
git push
```

### 2. Update the package version

Edit both:
- `pyproject.toml`: `version = "0.2.0"`
- `stp_database/__init__.py`: `__version__ = "0.2.0"`

### 3. Update in your bots

```bash
# Using UV
uv add --upgrade git+https://github.com/ERTG-BOTS/stp-database.git

# Using pip
pip install --upgrade --force-reinstall git+https://github.com/ERTG-BOTS/stp-database.git
```

## Authentication for Private Repositories

### Option 1: SSH (Recommended)

1. Setup SSH key on GitHub
2. Use SSH URL: `git+ssh://git@github.com/your-org/stp-database.git`

### Option 2: Personal Access Token

1. Create a GitHub Personal Access Token (PAT) with `repo` access
2. Install using:

```bash
uv add git+https://<TOKEN>@github.com/your-org/stp-database.git
```

Or in `pyproject.toml`:
```toml
[project]
dependencies = [
    "stp-database @ git+https://<TOKEN>@github.com/your-org/stp-database.git",
]
```

## Troubleshooting

### Import errors after installation

Make sure you've updated all imports from `infrastructure.database` to `stp_database`.

### Authentication errors

Ensure you have access to the private repository and your SSH keys or PAT are configured correctly.

### Version not updating

Use `--force-reinstall` flag:
```bash
pip install --upgrade --force-reinstall git+https://github.com/ERTG-BOTS/stp-database.git
```

## Multiple Bots Using the Same Package

All your bots can now use the same database package:

```
Bot 1 (stpsher-bot)     ──┐
                          ├──→  stp-database (GitHub)
Bot 2 (another-bot)     ──┤
                          │
Bot 3 (new-bot)         ──┘
```

Changes to the database package are immediately available to all bots after they run `uv add --upgrade`.

## Next Steps

1. Remove the old `infrastructure/database` folder from your bot projects (after migration)
2. Add `stp-database` to your `.gitignore` if needed
3. Document any bot-specific database extensions
4. Setup CI/CD for automatic testing when database package changes

## Summary

You now have:
- ✅ A standalone, reusable database package
- ✅ Version control for database layer
- ✅ No code duplication across bots
- ✅ Easy updates and maintenance
- ✅ Type-safe repository pattern
- ✅ Clean separation of concerns
