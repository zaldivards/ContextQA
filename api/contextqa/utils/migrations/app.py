import subprocess
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def check_migrations(*_):
    """Apply migrations if necessary"""
    if not _migrations_already_applied():
        code = subprocess.check_call(["alembic", "upgrade", "head"])
        logger.info("Migration finished with exit code: %i", code)
    yield
    logger.info("Terminating...")
