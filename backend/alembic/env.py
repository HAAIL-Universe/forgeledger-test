"""Alembic environment configuration for ForgeLedger Test.

Loads DATABASE_URL from environment variables (via dotenv) and configures
the Alembic migration context for both offline (SQL generation) and online
(direct database connection) modes.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

# ---------------------------------------------------------------------------
# Ensure the backend package is importable when running alembic CLI from
# the backend/ directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env file so DATABASE_URL is available even when invoked via CLI
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ---------------------------------------------------------------------------
# Alembic Config object – provides access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Target metadata – import your SQLAlchemy MetaData here if using
# autogenerate.  For now we use raw SQL migrations so this is None.
# ---------------------------------------------------------------------------
target_metadata = None


def _get_database_url() -> str:
    """Resolve the database URL from environment or alembic.ini.

    Priority:
        1. DATABASE_URL environment variable
        2. ``sqlalchemy.url`` in alembic.ini

    The asyncpg driver prefix (``postgresql+asyncpg://``) is normalised to
    the synchronous ``postgresql://`` scheme because Alembic runs migrations
    synchronously.

    Returns:
        A valid synchronous PostgreSQL connection string.

    Raises:
        RuntimeError: If no database URL can be resolved.
    """
    url: str | None = os.environ.get("DATABASE_URL")

    if url is None:
        url = config.get_main_option("sqlalchemy.url")

    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set and sqlalchemy.url "
            "is not configured in alembic.ini. Cannot run migrations."
        )

    # Normalise driver variants to plain psycopg2/libpq compatible URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif url.startswith("postgres://"):
        # Heroku-style URLs; SQLAlchemy 1.4+ requires ``postgresql://``
        url = url.replace("postgres://", "postgresql://", 1)

    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well. By skipping the Engine creation we
    don't even need a DBAPI to be available.

    Calls to ``context.execute()`` here emit the given string to the script
    output.
    """
    url = _get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates a synchronous SQLAlchemy engine, connects to the database, and
    runs all pending migrations inside a transaction.
    """
    url = _get_database_url()

    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        # Neon requires SSL in production; the sslmode param in the URL
        # handles this, but we pass isolation_level for clean transactions.
        isolation_level="AUTOCOMMIT",
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


# ---------------------------------------------------------------------------
# Entrypoint – Alembic calls this module; detect mode and dispatch.
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
