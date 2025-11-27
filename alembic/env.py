from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importa il Base dei tuoi modelli
from app.database.base import Base

# Importa i modelli per Alembic
# In questo modo Alembic conosce tutte le tabelle esistenti
from app.database import models  # assicura che tutti i modelli vengano importati

# Configurazione Alembic
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata per autogenerate
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
