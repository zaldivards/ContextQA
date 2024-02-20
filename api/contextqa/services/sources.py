from typing import Iterable

from sqlalchemy.orm import Session

from contextqa.models.orm import Source


def sources_exists(session: Session) -> bool:
    """Check if there is at least one source available

    Parameters
    ----------
    session : Session
        sqlalchemy session

    Returns
    -------
    bool
    """
    return session.query(Source.id).limit(1).count() > 0


def _sources_count(session: Session) -> int:
    return session.query(Source.id).count()


def get_sources(session: Session, limit: int, offset: int) -> tuple[Iterable[Source], int]:
    """Get a list of sources and the total number of sources

    Parameters
    ----------
    session : Session
        sqlalchemy session
    limit : int
        number of sources to return
    offset : int
        number of sources to skip

    Returns
    -------
    tuple[Iterable[Source], int]
    """
    return session.query(Source).offset(offset).limit(limit), _sources_count(session)
