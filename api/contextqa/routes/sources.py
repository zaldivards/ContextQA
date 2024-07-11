from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile, Depends, status, Query
from sqlalchemy.orm import Session

from contextqa import logger
from contextqa.models.schemas import SourceStatus, IngestionResult, Source, SourcesList
from contextqa.routes.dependencies import get_db, StoreClient, store_client, context_manager, session_generator
from contextqa.services import context
from contextqa.services.sources import sources_exists, get_sources, remove_sources
from contextqa.utils.exceptions import VectorDBConnectionError, DuplicatedSourceError


router = APIRouter()


@router.post("/ingest/", response_model=IngestionResult)
def ingest_source(
    documents: list[UploadFile],
    manager: Annotated[context.BatchProcessor, Depends(context_manager)],
):
    """Ingest sources used by the QA session"""
    try:
        processor = context.BatchProcessor(manager=manager, session_generator=session_generator)
        # pylint: disable=E1102
        return processor.persist(documents)
    except DuplicatedSourceError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "The source already exists and it doesn't have updated content",
                "cause": str(ex),
            },
        ) from ex
    except VectorDBConnectionError as ex:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={
                "message": (
                    "Connection error trying to set the context using the selected vector store. Please double check"
                    " your credentials"
                ),
                "cause": str(ex),
            },
        ) from ex
    except Exception as ex:
        logger.exception("Error while setting context. Cause: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex


@router.get("/check-availability/", response_model=SourceStatus)
async def check_sources(session: Annotated[Session, Depends(get_db)]):
    """Check the availability of at least one source"""
    try:
        status_flag = sources_exists(session)
        return SourceStatus.from_count_status(status_flag)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA could not get the results from the DB", "cause": str(ex)},
        ) from ex


@router.get("/", response_model=SourcesList)
async def get_active_sources(
    session: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1)] = 10,
    skip: Annotated[int, Query(ge=0)] = 0,
    query: Annotated[str | None, Query()] = None,
):
    """List active sources"""
    try:
        sources, total = get_sources(session, limit, skip, query)
        return SourcesList(
            sources=[Source(id=source.id, title=source.name, digest=source.digest) for source in sources], total=total
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA could not get the results from the DB", "cause": str(ex)},
        ) from ex


@router.post("/remove/")
async def remove_active_sources(
    sources: list[str],
    session: Annotated[Session, Depends(get_db)],
    client: Annotated[StoreClient | None, Depends(store_client)],
):
    """Remove active sources from both the relational and vector databases"""
    if not client:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"message": "Vector DB is unreachable"},
        )
    try:
        return {"removed": remove_sources(session, sources, client)}
    except Exception as ex:
        logger.error("Error removing sources. Reason: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA could not get the results from the DB", "cause": str(ex)},
        ) from ex
