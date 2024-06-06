from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextqa import settings


engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True, max_overflow=15)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def session_factory():
    """Session factory to avoid using a global session

    Returns
    -------
    Session
    """
    new_engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True, max_overflow=15)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
    return session_local()


def migration_session(url: str):
    """Prepare session for migrating to a different DB

    Returns
    -------
    Session
    """
    new_engine = create_engine(url, pool_pre_ping=True, max_overflow=15)
    return sessionmaker(autocommit=False, autoflush=False, bind=new_engine)()
