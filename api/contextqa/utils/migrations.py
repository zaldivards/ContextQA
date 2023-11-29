import subprocess
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, Table

from contextqa import settings


def _migrations_already_applied():
    engine = create_engine(settings.sqlalchemy_url)
    metadata = MetaData()

    # Pass the 'bind' argument when creating the Table
    version_table = Table("alembic_version", metadata, autoload=True, bind=engine)

    return version_table.exists()


@asynccontextmanager
async def check_migrations():
    """Apply migrations if necessary"""
    if not _migrations_already_applied():
        code = subprocess.check_call(["alembic", "upgrade", "head"])
        print("Migration finished with exit code:", code)
    yield
    print("Terminating...")
