from fastapi import APIRouter, HTTPException, UploadFile

from contextqa import context, get_logger
from contextqa.parsers.models import (
    LLMResult,
    QAResult,
    SimilarityProcessor,
    LLMContextQueryRequest,
)

LOGGER = get_logger()


router = APIRouter()


@router.post("/ingest/", response_model=LLMResult)
def ingest_source(
    document: UploadFile,
):
    """
    Set the document context to query it using the LLM and the vector store/processor

    **NOTE**: You need to set the following to use the pinecone vector store/processor:
    1. `PINECONE_TOKEN`
    2. `PINECONE_INDEX`
    3. `PINECONE_ENVIRONMENT_REGION`
    """
    try:
        context_setter = context.get_setter(SimilarityProcessor.LOCAL)
        # pylint: disable=E1102
        return context_setter.persist(document.filename, document.file)
    except context.VectorStoreConnectionError as ex:
        raise HTTPException(
            status_code=424,
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
            status_code=424,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex


@router.post("/", response_model=QAResult)
def qa(params: LLMContextQueryRequest):
    """
    Perform a QA process against the documents you have ingested
    """
    try:
        context_setter = context.get_setter(params.processor)
        # pylint: disable=E1102
        return context_setter.load_and_respond(params.question)
    except Exception as ex:
        raise HTTPException(
            status_code=424,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
