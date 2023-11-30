import subprocess
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import NoSuchTableError

from contextqa import settings


def _migrations_already_applied() -> bool:
    engine = create_engine(settings.sqlalchemy_url)
    metadata = MetaData()

    # Pass the 'bind' argument when creating the Table
    try:
        Table("alembic_version", metadata, autoload_with=engine)
    except NoSuchTableError:
        return False
    return True


@asynccontextmanager
async def check_migrations(*_):
    """Apply migrations if necessary"""
    if not _migrations_already_applied():
        code = subprocess.check_call(["alembic", "upgrade", "head"])
        print("Migration finished with exit code:", code)
    yield
    print("Terminating...")
