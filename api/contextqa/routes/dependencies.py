from typing import Generator

from contextqa.services.db import SessionLocal
from sqlalchemy.orm import scoped_session


def get_db() -> Generator:
    """DB session manager

    Yields
    ------
    Generator
        db session
    """
    try:
        session = scoped_session(SessionLocal)
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
