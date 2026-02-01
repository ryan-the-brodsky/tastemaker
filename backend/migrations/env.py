import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

from db_config import Base
from config import settings
from models import UserModel, ExtractionSessionModel, ComparisonResultModel, StyleRuleModel, GeneratedSkillModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url():
    """
    Get database URL from config settings.

    Priority:
    1. DATABASE_URL environment variable (loaded by config)
    2. Fallback to alembic.ini setting
    """
    # Use settings which handles normalization (postgres:// -> postgresql://)
    return settings.normalized_database_url


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    database_url = get_database_url()

    # Configure engine based on database type
    connect_args = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
