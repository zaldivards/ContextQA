from typing import Iterable

from sqlalchemy.orm import Session

from contextqa.models.orm import Source, VectorStore, Index
from contextqa.utils.clients import StoreClient
from contextqa.utils.settings import get_or_set


def _main_filter_query(session: Session, expresion):
    store_settings = get_or_set(kind="store")
    index = (
        f'{store_settings.store_params.get("home", store_settings.store_params.get("environment"))}/'
        f'{store_settings.store_params.get("collection", store_settings.store_params.get("index"))}'
    )
    return (
        session.query(expresion)
        .join(Index)
        .join(VectorStore)
        .filter(
            Index.name == index,
            VectorStore.name == store_settings.store,
        )
    )


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
    query = _main_filter_query(session, Source.id)
    return query.limit(1).count() > 0


def _sources_count(session: Session, like_query: str | None) -> int:
    query = _main_filter_query(session, Source)
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
    query = _main_filter_query(session, Source)

    if like_query:
        query = query.filter(Source.name.ilike(f"%{like_query}%"))
    return query.offset(offset).limit(limit), _sources_count(session, like_query)


def remove_sources(session: Session, sources: list[str], client: StoreClient) -> int:
    """Remove all the provided sources

    Parameters
    ----------
    session : Session
        sqlalchemy session
    sources : list[str]
        list of source names
    client : StoreClient
        Specific store client
    """
    store_settings = get_or_set(kind="store")
    sources_to_remove = (
        session.query(Source.id)
        .join(Index)
        .join(VectorStore)
        .filter(
            Source.name.in_(sources),
            Index.name == store_settings.store_params.get("collection", "index"),
            VectorStore.name == store_settings.store,
        )
    )

    removed_sources = session.query(Source).filter(Source.id.in_(sources_to_remove)).delete(synchronize_session=False)

    chunks_to_remove = client.get_ids(sources)
    client.delete(chunks_to_remove)

    return removed_sources
