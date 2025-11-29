"""
Configuração do ambiente Alembic para migrations.
"""
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Importa os modelos para que o SQLModel os registre
from app.models import Imovel  # noqa: F401

# Carrega variáveis do .env
load_dotenv()

# Configuração do Alembic
config = context.config

# Carrega a URL do banco de dados do .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não definida no arquivo .env")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configura logging se existe arquivo de config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos modelos SQLModel para autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Executa migrations em modo 'offline'.

    Configura o contexto apenas com a URL e não com um Engine,
    embora um Engine também seja aceitável aqui.
    Ao pular a criação do Engine, não precisamos nem de um DBAPI disponível.

    Chamadas ao context.execute() emitem a string dada para a saída do script.
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
    """Executa migrations em modo 'online'.

    Neste cenário, precisamos criar um Engine e associar uma conexão com o contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Habilita render_as_batch para SQLite (suporte a ALTER COLUMN)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True  # Necessário para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
