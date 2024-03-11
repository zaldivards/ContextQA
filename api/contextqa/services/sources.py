from typing import Iterable

from chromadb import PersistentClient
from langchain.vectorstores.chroma import Chroma
from sqlalchemy.orm import Session

from contextqa import settings
from contextqa.models.orm import Source, VectorStore, Index
from contextqa.utils.settings import get_or_set


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


def _sources_count(session: Session, like_query: str | None) -> int:
    query = session.query(Source)
    if like_query:
        query = query.filter(Source.name.ilike(f"%{like_query}%"))
    return query.count()


def get_sources(session: Session, limit: int, offset: int, like_query: str | None) -> tuple[Iterable[Source], int]:
    """Get a list of sources and the total number of sources

    Parameters
    ----------
    session : Session
        sqlalchemy session
    limit : int
        number of sources to return
    offset : int
        number of sources to skip
    like_query: str | None

    Returns
    -------
    tuple[Iterable[Source], int]
    """
    store_settings = get_or_set(kind="store")
    query = (
        session.query(Source)
        .join(Index)
        .join(VectorStore)
        .filter(
            Index.name == store_settings["store_params"].get("collection", "index"),
            VectorStore.name == store_settings["store"],
        )
    )
    if like_query:
        query = query.filter(Source.name.ilike(f"%{like_query}%"))
    return query.offset(offset).limit(limit), _sources_count(session, like_query)


def remove_sources(session: Session, sources: list[str]) -> int:
    """Remove all the provided sources

    Parameters
    ----------
    session : Session
        sqlalchemy session
    sources : list[str]
        list of source names
    """
    store_settings = get_or_set(kind="store")
    home = str(store_settings["store_params"]["home"])
    chroma_client = PersistentClient(path=home)
    sources_to_remove = (
        session.query(Source.id)
        .join(Index)
        .join(VectorStore)
        .filter(
            Source.name.in_(sources),
            Index.name == store_settings["store_params"].get("collection", "index"),
            VectorStore.name == store_settings["store"],
        )
    )

    removed_sources = session.query(Source).filter(Source.id.in_(sources_to_remove)).delete(synchronize_session=False)

    chunks_to_remove = []
    vector_store = Chroma(
        client=chroma_client,
        collection_name=store_settings["store_params"]["collection"],
        persist_directory=home,
    )
    for source in sources:
        if source.endswith(".pdf"):
            source = f"{settings.media_home}/{source}"
        chunks = vector_store.get(where={"source": source})
        chunks_to_remove.extend(chunks["ids"])

    vector_store.delete(chunks_to_remove)

    return removed_sources
