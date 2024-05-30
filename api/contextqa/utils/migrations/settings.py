from sqlalchemy.orm import Session
from sqlalchemy import MetaData, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from contextqa import logger
from contextqa.services.db import migration_session


def migrate_db(current_session: Session, url: str):
    """Migrate the database to a different DB

    Parameters
    ----------
    current_session : Session
        The current SQLAlchemy session connected to the original database
    url : str
        The URL of the new database to migrate to

    Raises
    ------
    ex : SQLAlchemyError
        If an error occurs during the migration process
    """
    fk_order = ("alembic_version", "store", "index", "sources")
    metadata = MetaData()
    metadata.reflect(bind=current_session.bind)
    migration_session_ = migration_session(url)
    metadata.create_all(migration_session_.bind)
    try:
        for table_name in fk_order:
            table = metadata.tables[table_name]
            data = current_session.execute(select(table))
            columns = [column.name for column in table.columns]
            rows = [dict(zip(columns, row)) for row in data]
            try:
                migration_session_.execute(table.insert().values(rows))
            except IntegrityError as ex:
                if table_name not in ("alembic_version", "store"):
                    raise ex
        migration_session_.commit()
    except SQLAlchemyError as ex:
        migration_session_.rollback()
        logger.exception(ex)
        raise ex
    else:
        logger.info("Database successfully migrated")
    finally:
        migration_session_.close()
