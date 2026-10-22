from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import your application's base model registry
from data.db_models import Base

 
from dotenv import load_dotenv
load_dotenv()  #

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Dynamically grab the connection string from your system environment
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Track your application's metadata for autogenerate detection
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # 1. Fetch the dictionary containing configuration blocks from alembic.ini
    alembic_config = config.get_section(config.config_ini_section) or {}

    # 2. Inject the runtime URL from memory into the parser dictionary.
    # This prevents KeyErrors if the line is commented out in alembic.ini.
    alembic_config["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    # 3. Create the database engine object safely
    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
