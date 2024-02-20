from typing import Iterable

from langchain.vectorstores.chroma import Chroma
from sqlalchemy.orm import Session

from contextqa import settings
from contextqa.models.orm import Source
from contextqa.services.context import chroma_client


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


def remove_sources(session: Session, sources: list[str]) -> int:
    """Remove all the provided sources

    Parameters
    ----------
    session : Session
        sqlalchemy session
    sources : list[str]
        list of source names
    """
    removed_sources = session.query(Source).filter(Source.name.in_(sources)).delete()
    chunks_to_remove = []
    vector_store = Chroma(
        client=chroma_client,
        collection_name=settings.default_collection,
        persist_directory=str(settings.local_vectordb_home),
    )
    for source in sources:
        if source.endswith(".pdf"):
            source = f"{settings.media_home}/{source}"
        chunks = vector_store.get(where={"source": source})
        chunks_to_remove.extend(chunks["ids"])

    vector_store.delete(chunks_to_remove)

    return removed_sources
