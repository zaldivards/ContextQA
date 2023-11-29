from typing import Generator

from contextqa.services.db import SessionLocal


def get_db() -> Generator:
    try:
        session = SessionLocal()
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
