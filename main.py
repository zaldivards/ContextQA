from fastapi import APIRouter, FastAPI, Form, HTTPException, Query, UploadFile

# pylint: disable=C0413
from retriever import models, social_media, vector

router = APIRouter()

app = FastAPI(title="LLM Retriever", openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc")


@app.get("/social-media", response_model=models.Summary)
def get_user_info(name: str = Query(min_length=4)):
    try:
        return social_media.seach_user_info(name)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@router.post("", response_model=models.VectorScanResult)
def query_text(params: models.LLMQueryTextRequestBody):
    try:
        return vector.simple_scan(params)
    except Exception as ex:
        raise HTTPException(status_code=424, detail={"message": "Something went wrong", "cause": str(ex)}) from ex


@router.post("/document", response_model=models.VectorScanResult)
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


@router.post("/pdf", response_model=models.VectorScanResult)
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


app.include_router(router, prefix="/context-query", tags=["Queries with context"])
