# pylint: disable=C0413
from fastapi import APIRouter, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from contextqa import chat, context, get_logger, models

LOGGER = get_logger()

one_time_router = APIRouter()
context_router = APIRouter()

app = FastAPI(title="ContextQA api", openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc")
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/ping")
def ping():
    """Test whether the api is up and running"""
    return "Pong!"


@app.post("/qa", response_model=models.LLMResult)
def llm_qa(params: models.LLMQueryRequest):
    """
    Provide a message and receive a response from the LLM
    """
    try:
        return chat.qa_service(params.message)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@context_router.post("/set", response_model=models.LLMResult)
def set_context(
    document: UploadFile,
    separator: str = Form(default="."),
    chunk_size: int = Form(default=100),
    chunk_overlap: int = Form(default=50),
    similarity_processor: models.SimilarityProcessor = Form(default="local"),
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
            models.LLMRequestBodyBase(
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


@context_router.post("/query", response_model=models.LLMResult)
def query_llm(params: models.LLMContextQueryRequest):
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


app.include_router(one_time_router, prefix="/query", tags=["Queries with one-time context"])
app.include_router(context_router, prefix="/context", tags=["Queries with persistent context"])
