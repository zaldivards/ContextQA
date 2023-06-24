from typing import Optional

from fastapi import APIRouter, FastAPI, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# pylint: disable=C0413
from retriever import context, models, social_media, vector

one_time_router = APIRouter()
context_router = APIRouter()

app = FastAPI(title="LLM Retriever", openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc")
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/social-media", response_model=models.Summary)
def get_user_info(name: str = Query(min_length=4)):
    try:
        return social_media.seach_user_info(name)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@one_time_router.post("", response_model=models.VectorScanResult)
def query_text(params: models.LLMQueryTextRequestBody):
    try:
        return vector.simple_scan(params)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@one_time_router.post("/document", response_model=models.VectorScanResult)
def query_document(
    document: UploadFile,
    query: str = Form(min_length=10),
    separator: str = Form(default="."),
    chunk_size: int = Form(default=100),
    similarity_processor: models.SimilarityProcessor = Form(default="local"),
):
    try:
        return vector.document_scan(
            models.LLMQueryDocumentRequestBody(
                query=query, separator=separator, chunk_size=chunk_size, similarity_processor=similarity_processor
            ),
            document.file,
        )
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@one_time_router.post("/pdf", response_model=models.VectorScanResult)
def query_pdf(
    document: UploadFile,
    query: str = Form(min_length=10),
    separator: str = Form(default="."),
    chunk_size: int = Form(default=100),
    similarity_processor: models.SimilarityProcessor = Form(default="local"),
):
    try:
        return vector.pdf_scan(
            models.LLMQueryDocumentRequestBody(
                query=query, separator=separator, chunk_size=chunk_size, similarity_processor=similarity_processor
            ),
            document.file,
        )
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@context_router.post("/set", response_model=models.VectorScanResult)
def set_context(
    document: UploadFile,
    separator: str = Form(default="."),
    chunk_size: int = Form(default=100),
    chunk_overlap: int = Form(default=50),
    similarity_processor: models.SimilarityProcessor = Form(default="local"),
):
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
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@context_router.get("/query", response_model=models.VectorScanResult)
def query_llm(question: str, processor: models.SimilarityProcessor, identifier: Optional[str] = None):
    try:
        context_setter = context.get_setter(processor)
        # pylint: disable=E1102
        return context_setter.load_and_respond(question, identifier)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


app.include_router(one_time_router, prefix="/query", tags=["Queries with one-time context"])
app.include_router(context_router, prefix="/context", tags=["Queries with persistent context"])
