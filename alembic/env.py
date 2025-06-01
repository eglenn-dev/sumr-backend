import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine as app_engine
from sqlmodel import SQLModel 
from app.models import User, Book, Transaction

target_metadata = SQLModel.metadata 

def get_url():
    from app.core.config import settings
    return str(settings.LOCAL_DATABASE_URL or settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    # ... (rest of the function remains the same)
    """
    url = get_url() 
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    # ... (rest of the function remains the same)
    """
    DB_URL = get_url() 
    
    if not config.get_main_option("sqlalchemy.url"):
        config.set_main_option("sqlalchemy.url", DB_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
        )
