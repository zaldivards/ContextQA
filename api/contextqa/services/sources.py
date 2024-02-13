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


def get_sources(session: Session, limit: int, offset: int) -> Iterable[Source]:
    """Get a list of sources

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
    Iterable[Source]
    """
    return session.query(Source).offset(offset).limit(limit)
