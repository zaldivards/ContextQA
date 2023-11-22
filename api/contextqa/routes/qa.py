from fastapi import APIRouter, Form, HTTPException, UploadFile

from contextqa import context, get_logger
from contextqa.parsers.models import (
    LLMResult,
    QAResult,
    SimilarityProcessor,
    LLMRequestBodyBase,
    LLMContextQueryRequest,
)

LOGGER = get_logger()


router = APIRouter()


@router.post("/ingest", response_model=LLMResult)
def ingest_source(
    document: UploadFile,
    separator: str = Form(default="."),
    chunk_size: int = Form(default=100),
    chunk_overlap: int = Form(default=50),
    similarity_processor: SimilarityProcessor = Form(default="local"),
):
    """
    Set the document context to query it using the LLM and the vector store/processor

    **NOTE**: You need to set the following to use the pinecone vector store/processor:
    1. `PINECONE_TOKEN`
    2. `PINECONE_INDEX`
    3. `PINECONE_ENVIRONMENT_REGION`
    """
    try:
        context_setter = context.get_setter(similarity_processor)
        # pylint: disable=E1102
        return context_setter.persist(
            document.filename,
            LLMRequestBodyBase(
                separator=separator,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            document.file,
        )
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
    Perform a query against the document context

    **Note**: The `processor` and `identifier` parameters must be the same you set with the `/context/set` endpoint.
    The `identifier` parameter was set using the provided document's name
    """
    try:
        context_setter = context.get_setter(params.processor)
        # pylint: disable=E1102
        return context_setter.load_and_respond(params.question, params.identifier)
    except Exception as ex:
        raise HTTPException(
            status_code=424,
            detail={"message": "ContextQA server did not process the request successfully", "cause": str(ex)},
        ) from ex
