from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile, Depends, status
from sqlalchemy.orm import Session

from contextqa import context, get_logger
from contextqa.models.schemas import (
    LLMResult,
    QAResult,
    SimilarityProcessor,
    LLMContextQueryRequest,
)
from contextqa.routes.dependencies import get_db
from contextqa.utils.exceptions import VectorDBConnectionError, DuplicatedSourceError

LOGGER = get_logger()


router = APIRouter()


@router.post("/ingest/", response_model=LLMResult)
def ingest_source(document: UploadFile, session: Annotated[Session, Depends(get_db)]):
    """
    Ingest a data source into the vector database
    """
    try:
        context_setter = context.get_setter(SimilarityProcessor.LOCAL)
        # pylint: disable=E1102
        return context_setter.persist(document.filename, document.file, session)
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
        LOGGER.exception("Error while setting context. Cause: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex


@router.post("/", response_model=QAResult)
def qa(params: LLMContextQueryRequest):
    """
    Perform a QA process against the documents you have ingested
    """
    try:
        context_setter = context.get_setter()
        # pylint: disable=E1102
        return context_setter.load_and_respond(params.question)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
