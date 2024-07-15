from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import NoSuchTableError

from contextqa import settings, logger


def _migrations_already_applied() -> bool:
    engine = create_engine(settings.sqlalchemy_url)
    metadata = MetaData()
    try:
        Table("alembic_version", metadata, autoload_with=engine)
    except NoSuchTableError:
        return False
    except Exception as ex:
        logger.error("Migration check failed. Cause %s", ex)
    return True


def run_migrations() -> None:
    """Run initial migrations"""
    script_location = str(Path(__file__).parent.parent.parent / "alembic")
    logger.info("Running initial migrations...")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", settings.sqlalchemy_url)
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def check_migrations(*_):
    """Apply migrations if necessary"""
    if not _migrations_already_applied():
        run_migrations()
    yield
    logger.info("Terminating...")
